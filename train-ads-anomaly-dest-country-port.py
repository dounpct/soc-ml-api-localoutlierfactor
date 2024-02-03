import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from sklearn import metrics

########### mflow ############
import mlflow
import mlflow.sklearn
########### mflow ############
from sharelib import *
from report import *
from pathlib import Path
import json
import glob
import sys
import pickle

jenkinsURL = getArgs(1,"")
mlflowMinioFolder = getArgs(2,"")
mlflowTrainingFileLimit = int(getArgs(3,10))
jenkinsBuildID = getArgs(4,"")

if __name__ == "__main__": 
    df = pd.DataFrame()
    path_to_json = 'rawdata' 
    json_pattern = os.path.join(path_to_json,'*.txt')
    file_list = glob.glob(json_pattern)
    
    xcount = 0

    for file in file_list:
        xcount = xcount + 1
        print("xcount: ", xcount)
        data = pd.read_json(file, lines=True)
        df = pd.concat([df,data], ignore_index = True)
        if (xcount == mlflowTrainingFileLimit):
            break
    
    
    np.set_printoptions(threshold=sys.maxsize)

    # df_categories = df[df["ads_country_dst"].str.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')) == False] 
    df_categories = pd.concat([df["ads_country_dst"]], axis=1, sort=False,)
    print("-------------- Count Record --------------")
    print(df_categories.shape[0])
    print("-------------- Count Record --------------")
    print("-------------- Count Destination Country --------------")
    print(df_categories.value_counts().to_string())
    print("-------------- Count Destination Country --------------")
    
    countryMap = mapOfCountryDst()
    portMap = mapOfPort()
    print("-------------- Number of Country in Encoding --------------")
    print("country_key : ", len(countryMap.keys()))
    print("country_count : ", len(set(countryMap.values())))
    print("-------------- Number of Country in Encoding --------------")
    print("-------------- Show Country Not in list --------------")
    print(df_categories[~df_categories['ads_country_dst'].isin(countryMap.keys())].value_counts().to_string())
    print("-------------- Show Country Not in list --------------")

    df_categories = df_categories.mask(~df_categories.isin(countryMap.keys()),'OTHER')
    print("Mask OTHER done")
    X = df_categories.replace({'ads_country_dst': countryMap})
    print("Frequency encoding done")
    
    df_categories = pd.concat([df_categories,df["ads_dst_port"]], axis=1, sort=False,)
    ads_dst_port = pd.concat([df["ads_dst_port"]], axis=1, sort=False,).astype(str)
    ads_dst_port = ads_dst_port.mask(~ads_dst_port.isin(portMap.keys()), 'OTHER')
    ads_dst_port = ads_dst_port.replace({'ads_dst_port': portMap})
    
    X = pd.concat([X,ads_dst_port], axis=1, sort=False,)

    normalPoint = 30
    mask = (X['ads_country_dst'] <= normalPoint) & (X['ads_dst_port'] == 0)
    X_Test = pd.DataFrame({'test': [-1] * len(df)})
    X_Test.loc[mask, 'test'] = 1
    
    # Call and fit the Local Outlier Factor detector
    setNNeighbors = int((df_categories.shape[0]/300)) # /30 This is best scenario but memory 64GB still OMM killed
    print("set n_neighbors : " , setNNeighbors)
    lof_detector = LocalOutlierFactor(n_neighbors=setNNeighbors, contamination=0.1,novelty=True).fit(X.values)
    print("-------------- Model Size (MB) --------------")
    print("{:.2f}".format(sys.getsizeof(pickle.dumps(lof_detector))/(1024*1024)))
    print("-------------- Model Size (MB) --------------")
    lof_detect = lof_detector.predict(X)

    recordDetect,countDetect = np.unique(lof_detect, return_counts=True)
    print("--------------Count Anomaly VS Normal-------------")
    print(recordDetect)
    print(countDetect)

    if (len(countDetect) == 1):
        row_to_be_added = countDetect
        countDetect = np.append(np.array([0]),row_to_be_added,axis=0)

    print("Anomaly = " , countDetect[0] , "record with " , (countDetect[0])*100/(countDetect[0]+countDetect[1]) ," %")
    print("Normal  = " , countDetect[1] , "record with " , (countDetect[1])*100/(countDetect[0]+countDetect[1]) ," %")
    htmlAnomalyVSNormally = '''
    <table class="table table-striped">
        <th>Type</th><th class=right-aligned>Record</th><th class=right-aligned>%Record</th>
        <tr><td>Anomaly</td><td class=right-aligned>''' + str(countDetect[0]) + '''</td><td class=right-aligned> ''' + str((countDetect[0])*100/(countDetect[0]+countDetect[1])) + '''</td></tr>
        <tr><td>Normal</td><td class=right-aligned>''' + str(countDetect[1]) + '''</td><td class=right-aligned> ''' + str((countDetect[1])*100/(countDetect[0]+countDetect[1])) + '''</td></tr>
    </table>
    '''
    print("--------------Count Anomaly VS Normal-------------")
    print("-------------- List Destination Country Port with Prediction  -------------")
    # print(type(df_categories.value_counts()))
    # print(type(df_categories))
    htmlItem = ""
    for index, value in df_categories.value_counts().items():
        encode = countryMap[index[0]]

        portEncode = 0
        if (str(index[1]) in portMap):
            portEncode = portMap[str(index[1])]

        predictData = lof_detector.predict([[ encode , portEncode ]])

    # if (portEncode > 0 and predictData[0] == 1):
        print(index[0]  , " | code =" , encode , " | Port Level = ", index[1] , "/" , str(portEncode)  , " | count ="  , value , " | result =" , dataPredictionToString(predictData[0]))
    
        htmlItem = htmlItem + "<tr><td>" + index[0] + "</td><td class=right-aligned>" + str(encode) + "</td><td class=right-aligned>" + str(index[1]) + "</td><td class=right-aligned>" + str(portEncode) + "</td><td class=right-aligned>" + str(value)+ "</td><td>" + dataPredictionToString(predictData[0]) + "</td><tr>"
    print("-------------- List Destination Country with Prediction -------------")

    htmlCountryPrediction = '''
    <table class="table table-striped">
        <th>Country</th><th class=right-aligned>CODE</th><th class=right-aligned>Port</th><th class=right-aligned>Malware DST Ports Level</th><th class=right-aligned>Amount</th><th>Prediction</th>
        ''' + htmlItem + '''
    </table>
    '''
    print("-------------- List Destination Country Port with Prediction -------------")
    
    plt.figure(figsize=(7,7))
    plt.scatter(X.to_numpy()[:, 0], X.to_numpy()[:, 1], c=lof_detect, cmap="flag", alpha=0.7)
    plt.title("train-ads-anomaly-dest-country-port")
    plt.savefig('images/train-ads-anomaly-dest-country-port.png')
    plt.show()

    print("-------------- Machine Learning - Confusion Matrix -------------")
    Accuracy = metrics.accuracy_score(X_Test, lof_detect)
    print("Accuracy : " , Accuracy)
    Precision = metrics.precision_score(X_Test, lof_detect)
    print("Precision : " , Precision)
    Sensitivity_recall = metrics.recall_score(X_Test, lof_detect)
    print("Sensitivity_recall : " , Sensitivity_recall)
    Specificity = metrics.recall_score(X_Test, lof_detect, pos_label=-1)
    print("Specificity : " , Specificity)
    F1_score = metrics.f1_score(X_Test, lof_detect)
    print("F1_score : " , F1_score)

    htmlMatrix = '''
    <table class="table table-striped">
        <th>Type</th><th>Meaning</th><th class=right-aligned>Score</th>
        <tr><td>Accuracy</td><td>The proportion of correctly predicted cases</td><td class=right-aligned>''' + str(Accuracy) + '''</td></tr>
        <tr><td>Precision</td><td>Positive Predictive Value</td><td class=right-aligned>''' + str(Precision) + '''</td></tr>
        <tr><td>Sensitivity_recall</td><td> True Positive Rate</td><td class=right-aligned>''' + str(Sensitivity_recall) + '''</td></tr>
        <tr><td>Specificity</td><td>True Negative Rate</td><td class=right-aligned>''' + str(Specificity) + '''</td></tr>
        <tr><td>F1_score</td><td>Balances precision and recall</td><td class=right-aligned>''' + str(F1_score) + '''</td></tr>    
    </table>
    '''
    print("-------------- Machine Learning - Confusion Matrix -------------")


    confusion_matrix = metrics.confusion_matrix(X_Test, lof_detect)
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = confusion_matrix, display_labels = ["Anomally", "Normally"])
    cm_display.plot()
    plt.savefig('images/train-ads-anomaly-dest-country-port-confusion-matrix.png')
    plt.show()

    summary_table = '''
    <p>Count Record : ''' + str(df_categories.shape[0]) + '''</p>
    <h2>Local Outlier Factor (LOF)</h2>
    <p>n_neighbors : ''' + str(setNNeighbors) + '''</p>
    ''' + htmlAnomalyVSNormally + '''
    ''' + htmlCountryPrediction + '''
    <table class="table table-striped">
    <th>Local Outlier Factor (LOF)</th>
    <tr>
        <td><img src="train-ads-anomaly-dest-country-port.png" alt="train-ads-anomaly-dest-country-port.png"></td>
    </tr>
        </table>
    <table class="table table-striped">
    <th>confusion-matrix</th>
    <tr>
        <td><img src="train-ads-anomaly-dest-country-port-confusion-matrix.png" alt="confusion-matrix"></td>
    </tr>
    </table>
    ''' + htmlMatrix + '''
    '''

    html_string = mainReportHTML("train-ads-anomaly-dest-country-port",summary_table)   

    f = open('report.html','w')
    f.write(html_string)
    f.close()

    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
    # export MLFLOW_TRACKING_USERNAME=user 
    # export MLFLOW_TRACKING_PASSWORD=pwd

    experiment = mlflow.set_experiment(experiment_name='ads-anomaly-dest-country-port')
    experiment_id = experiment.experiment_id

    reportURL = "https://minio-api.rtarf-ml.its-software-services.com/ml-report/train-ads-anomaly-dest-country-port/" + jenkinsBuildID + "/report.html"

    run_description = f"""
### Note
**All information** * about Training * ~~ML here~~
Jenkins URL: [{jenkinsURL}]({jenkinsURL})
Report: [{reportURL}]({reportURL})
    """

    with mlflow.start_run(experiment_id=experiment_id,description=run_description):
        mlflow.set_tracking_uri(tracking_uri)

        print("Artifact Location: {}".format(experiment.artifact_location))
        print("artifact uri : " + mlflow.get_artifact_uri())

        mlflow.doctor()
        
        mlflowMinioFolder
        mlflow.log_param("MlflowMinioFolder", mlflowMinioFolder)
        mlflow.log_param("country_key", len(countryMap.keys()))
        mlflow.log_param("country_count", len(set(countryMap.values())))
        mlflow.log_param("SampleFiles", xcount)
        mlflow.log_param("SampleRows", X.shape[0])

        # mlflow.set_tag("JenkinsURL",jenkinsURL)
        mlflow.log_metric("Anomaly", str((countDetect[0])*100/(countDetect[0]+countDetect[1])))
        mlflow.log_metric("Normally", str((countDetect[1])*100/(countDetect[0]+countDetect[1])))
        mlflow.sklearn.log_model(lof_detector, "model", registered_model_name="ads-anomaly-by-dest-country-port")
        print("Model saved in run %s" % mlflow.active_run().info.run_uuid)