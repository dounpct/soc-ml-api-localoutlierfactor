from flask import Flask, request, jsonify
import requests
import json
from waitress import serve
import os

import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder
from sharelib import *

app = Flask(__name__)

host = os.environ.get('host_ml', 'mlflow-app.rtarf-ml.its-software-services.com')
port = os.environ.get('port_ml', '80')

host_anomaly_des_country = os.environ.get('host_anomaly_des_country', 'mlflow-ads-anomaly-dest-country.rtarf-ml.its-software-services.com')
port_anomaly_des_country = os.environ.get('port_anomaly_des_country', '80')
host_anomaly_des_country_port = os.environ.get('host_anomaly_des_country_port', 'mlflow-ads-anomaly-dest-country-port.rtarf-ml.its-software-services.com')
port_anomaly_des_country_port = os.environ.get('port_anomaly_des_country_port', '80')

host_anomaly_time = os.environ.get('host_anomaly_time', 'mlflow-ads-anomaly-time.rtarf-ml.its-software-services.com')
port_anomaly_time = os.environ.get('port_anomaly_time', '80')

gateway_port = os.environ.get('gateway_port_ml', '8082')

@app.route('/v3/gateway', methods=['GET'])
def get_MockData():

    mockData = {
                    "results": [
                        {
                            "subject": "supervised_dst_country_anomaly",
                            "result": "true",
                            "certainty": 0.99
                        },
                        {
                            "subject": "supervised_login_anomaly",
                            "result": "false",
                            "certainty": 1.00
                        },
                        {
                            "subject": "unsupervised_dst_country_anomaly",
                            "result": "Normally", #Anomaly
                            "certainty": 0.99
                        },
                        {
                            "subject": "unsupervised_login_anomaly",
                            "result": "Normally", #Anomaly
                            "certainty": 0.99
                        }
                    ]
                }

    jsonString = json.dumps(mockData, indent=4)
    
    return jsonString

def createDataAdsAnomalyDestCountry(request_country):
    
    test_df = pd.DataFrame([[request_country]],columns=['ads_country_dst'])
    
    test_df['ads_country_dst'] = test_df['ads_country_dst'].mask(~test_df['ads_country_dst'].isin(countryMap.keys()),'OTHER')
    X_new = test_df.replace({'ads_country_dst': countryMap})

    data = {
        "data":
        X_new.values.tolist()
    }

    return data

def createDataAdsAnomalyDestCountryPort(request_country,request_port):
    
    test_df = pd.DataFrame([[request_country,request_port]],columns=['ads_country_dst','ads_dst_port'])
    
    test_df['ads_country_dst'] = test_df['ads_country_dst'].mask(~test_df['ads_country_dst'].isin(countryMap.keys()),'OTHER')
    test_df['ads_dst_port'] = test_df['ads_dst_port'].mask(~test_df['ads_dst_port'].isin(portMap.keys()),'OTHER')

    X_new = test_df.replace({'ads_country_dst': countryMap})
    X_new = X_new.replace({'ads_dst_port': portMap})
    data = {
        "data":
        X_new.values.tolist()
    }

    return data

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    resp = jsonify(message="OK")
    resp.status_code = 200
    return resp

@app.route('/v5/gateway', methods=['POST'])
def get_invocationsV5():
    headers = {
        "Content-Type": "application/json",
    }

    predictionList = []
    content = request.json

    runAdsCountryDst = ('disable_predict_anomaly_dest_country' not in content) or (content['disable_predict_anomaly_dest_country'] != 'true')
    runAdsTime = ('disable_predict_anomaly_time' not in content) or (content['disable_predict_anomaly_time'] != 'true')
    ads_country_dst_log = ""
    ads_ts_hh_log = ""
    foundFlag = False
    if (runAdsCountryDst and ('ads_country_dst' in content)):
        content_data = createDataAdsAnomalyDestCountryPort(content['ads_country_dst'],content['ads_dst_port'])
        print(content_data)
        ads_country_dst_log = "ads_country_dst : ",content['ads_country_dst'],":",content['ads_dst_port']
        print(ads_country_dst_log)
        foundFlag = True
        try:
            resp = requests.post(
                url="http://%s:%s/invocations" % (host_anomaly_des_country_port, port_anomaly_des_country_port),
                data=json.dumps({"dataframe_split": content_data}),headers=headers,
            )
            responseData = {
                                "subject": "unsupervised_dst_country_anomaly",
                                "result": dataPredictionToString(resp.json()["predictions"][0])
                            }
            predictionList.append(responseData)
            print(ads_country_dst_log,"-",resp.status_code)
        except Exception as e:
            errmsg = "Caught exception attempting to call model endpoint: %s" % e
            print(errmsg, end="")
            return resp.json()

    if (runAdsTime and ('ads_ts_hh' in content)):
        content_data = {"data":[[ content['ads_ts_hh'] ]]}
        ads_ts_hh_log = "ads_ts_hh : ",content['ads_ts_hh']
        print(ads_ts_hh_log)
        foundFlag = True
        try:
            resp = requests.post(
                url="http://%s:%s/invocations" % (host_anomaly_time, port_anomaly_time),
                data=json.dumps({"dataframe_split": content_data}),headers=headers,
            )
            responseData = {
                                "subject": "unsupervised_login_anomaly",
                                "result": dataPredictionToString(resp.json()["predictions"][0])
                            }
            predictionList.append(responseData)
            print(ads_ts_hh_log,"-",resp.status_code)
        except Exception as e:
            errmsg = "Caught exception attempting to call model endpoint: %s" % e
            print(errmsg, end="")
            return resp.json()

    if (not foundFlag):
        print("request not invocate all ml")

    responsePredictData = {"results": predictionList}
    jsonString = jsonify(responsePredictData)
    print(ads_country_dst_log,"|", ads_ts_hh_log,"|",responsePredictData)
    return jsonString

if __name__ == '__main__':
    countryMap = mapOfCountryDst()
    portMap = mapOfPort()
    
    print("Server Ready On Port " + gateway_port)

    serve(app, host="0.0.0.0", port=gateway_port)
    