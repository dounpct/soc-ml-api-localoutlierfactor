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

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder

from sharelib import *
from report import *
import logging
from pathlib import Path
import json
import glob
import sys
import pickle

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

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
    
    df_categories = pd.concat([df["ads_ts_hh"]], axis=1, sort=False,)
    print("-------------- Count Record --------------")
    print(df_categories.shape[0])
    print("-------------- Count Record --------------")
    print("-------------- Count HH --------------")
    print(df_categories.value_counts().to_string())
    print("-------------- Count HH --------------")

    X = df_categories

    X_Test = X.mask((X >= 6) & (X <= 18), 99)
    X_Test.mask(X_Test < 99, -1,inplace=True)
    X_Test.mask(X_Test == 99, 1,inplace=True)

    X_Count = X.replace({'ads_ts_hh': X.value_counts().to_dict()})
    
    # Call and fit the Local Outlier Factor detector
    setNNeighbors = int((df_categories.shape[0]/3)) # /3 This is best scenario but memory 64GB still OMM killed
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
    print("--------------Count Anomaly VS Normal-------------")
    htmlAnomalyVSNormally = '''
    <table class="table table-striped">
        <th>Type</th><th class=right-aligned>Record</th><th class=right-aligned>%Record</th>
        <tr><td>Anomaly</td><td class=right-aligned>''' + str(countDetect[0]) + '''</td><td class=right-aligned> ''' + str((countDetect[0])*100/(countDetect[0]+countDetect[1])) + '''</td></tr>
        <tr><td>Normal</td><td class=right-aligned>''' + str(countDetect[1]) + '''</td><td class=right-aligned> ''' + str((countDetect[1])*100/(countDetect[0]+countDetect[1])) + '''</td></tr>
    </table>
    '''

    print("-------------- List HH with Prediction -------------")
    htmlItem = ""
    for index, value in df_categories.value_counts().items():
        tempdf = pd.DataFrame([
            [index[0]]
        ], columns=['ads_ts_hh'])
        predictData = lof_detector.predict(tempdf)
        print(index[0]  , " | count ="  , value , " | result =" , dataPredictionToString(predictData[0]))
        htmlItem = htmlItem + "<tr><td>" + str(index[0]) + "</td><td class=right-aligned>" + str(value)+ "</td><td>" + dataPredictionToString(predictData[0]) + "</td><tr>"

    print("-------------- List HH with Prediction -------------")

    htmlCountryPrediction = '''
    <table class="table table-striped">
        <th>HH</th><th class=right-aligned>Amount</th><th>Prediction</th>
        ''' + htmlItem + '''
    </table>
    '''

    plt.figure(figsize=(7,7))
    plt.scatter(X.to_numpy()[:, 0], X_Count.to_numpy()[:, 0], c=lof_detect, cmap="flag", alpha=0.5)
    plt.title("train-ads-anomaly-time")
    plt.savefig('images/train-ads-anomaly-time.png')
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
    print("-------------- Machine Learning - Confusion Matrix -------------")

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
    confusion_matrix = metrics.confusion_matrix(X_Test, lof_detect)
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = confusion_matrix, display_labels = ["Anomally", "Normally"])
    cm_display.plot()
    plt.savefig('images/train-ads-anomaly-time-confusion-matrix.png')
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
        <td><img src="train-ads-anomaly-time.png" alt="train-ads-anomaly-time.png"></td>
    </tr>
        </table>
    <table class="table table-striped">
    <th>confusion-matrix</th>
    <tr>
        <td><img src="train-ads-anomaly-time-confusion-matrix.png" alt="confusion-matrix"></td>
    </tr>
    </table>
    ''' + htmlMatrix + '''
    '''

    html_string = mainReportHTML("train-ads-anomaly-time",summary_table)
    f = open('report.html','w')
    f.write(html_string)
    f.close()

    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
    # export MLFLOW_TRACKING_USERNAME=user 
    # export MLFLOW_TRACKING_PASSWORD=pwd

    experiment = mlflow.set_experiment(experiment_name='ads-anomaly-time')
    experiment_id = experiment.experiment_id

    reportURL = "https://minio-api.rtarf-ml.its-software-services.com/ml-report/train-ads-anomaly-time/" + jenkinsBuildID + "/report.html"

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
        mlflow.log_param("MlflowMinioFolder", mlflowMinioFolder)
        mlflow.log_param("SampleFile", xcount)
        mlflow.log_param("SampleRows", X.shape[0])

        mlflow.log_metric("Anomaly", str((countDetect[0])*100/(countDetect[0]+countDetect[1])))
        mlflow.log_metric("Normal", str((countDetect[1])*100/(countDetect[0]+countDetect[1])))
        mlflow.sklearn.log_model(lof_detector, "model", registered_model_name="ads-anomaly-by-time")
        print("Model saved in run %s" % mlflow.active_run().info.run_uuid)