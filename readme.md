# Run on Local WSL Ubuntu 20.04 
## need python 3.9


    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt install python3.9
    python3.9 --version

    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.9 get-pip.py

    pip3.9 install -r requirements.txt
    
    ### please load firewall-traffic.csv to folder data
    python3.9 train.py

        mlflow ui
        export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
    or 
        mlflow server --host 0.0.0.0 -p 8889
        export MLFLOW_TRACKING_URI=http://127.0.0.1:8889
        export MLFLOW_TRACKING_URI=http://mlflow.rtarf-ml.its-software-services.com/

# Run mlflow

    mlflow server --host 0.0.0.0 -p 8889
    export MLFLOW_TRACKING_URI=http://127.0.0.1:8889
    
    mlflow run .
    mlflow run . --env-manager local
    mlflow models serve -m file:///mnt/d/work/mlflow/mlflow/examples/supply_chain_security/mlruns/0/2848e2593fc24c7cbcef69b5ad8ec148/artifacts/model -p 1234

    mlflow models serve -m mlflow-artifacts:/5/8911fc4e3a514e969cac16d157b008ed/artifacts/model -p 1236
    mlflow models serve -m mlflow-artifacts:/5/8911fc4e3a514e969cac16d157b008ed/artifacts/model -p 1236 --no-conda

# Test From PostMan

    http://127.0.0.1:1234/invocations

    {"dataframe_split": {"data":
    [   [ 13.72917 , 100.52389 ],
        [ 13.2434 ,  100.12212 ],
        [  1.234  ,  100.34344 ],
        [  1.234  ,   10.34344 ],
        [  1.234  ,   10.34344 ],
        [  1.234  ,   10.34344 ],
        [  1.234  ,  100.8     ],
        [  1.234  ,  100.09    ],
        [  1.234  ,   18.34344 ],
        [  1.234  ,   19.34994 ],
        [ 13.675776 , 100.423432]
    ]
    }}

    http://127.0.0.1:1234/invocations

    {"dataframe_split": {"data":[[
    
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
    0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  1.0,  0.0
    
    ]]}}

    {
        "predictions": [
            "yes"
        ]
    }

    ----------------------------------------------------------------------

    {"dataframe_split": {"data":[[
    
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
    0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
    0.0,  0.0,  0.0,  1.0
    
    ]]}}

    {
        "predictions": [
            "no"
        ]
    }

    ----------------------------------------------------------------------



# Test From Curl

## On Invocation
    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[                      \
        [13.72917 , 100.52389],
	    [13.12323 , 100.34343]
	]}}"    
                                   \
    http://127.0.0.1:1236/invocations | jq

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[                      \
        [ 196 ]
	]}}"                                   \
    http://mlflow-ads-anomaly-dest-country.rtarf-ml.its-software-services.com/invocations | jq

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[                      \
        [ 82 ]
	]}}"                                   \
    http://mlflow-ads-anomaly-dest-country.rtarf-ml.its-software-services.com/invocations | jq

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[[                          \
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  1.0,  0.0]]}}"                                      \
    http://127.0.0.1:1234/invocations | jq

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[[                          \
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  1.0,  0.0]]}}"                                      \
    http://mlflow-serving.mlflow-app.svc.cluster.local:8082/invocations | jq

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[[                          \
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  1.0,  0.0]]}}"                                      \
    http://mlflow-app.rtarf-ml.its-software-services.com/invocations | jq
    
    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"dataframe_split\": {\"data\":[[                          \
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.0,  0.0,  1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  
        0.0,  0.0,  1.0,  0.0]]}}"                                      \
    http://nginx-auth-test.tdg-int.net/invocations -u 'ingress_user:xxxxxxxxxxxxxxxxxxxxxx' | jq



## On Gateway

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"data\": {\"data\":[[\"Russian Federation\",\"yes\"]]}}"  \
    http://127.0.0.1:5000/gateway | jq

    {
        "predictions": [
            "no"
        ]
    }

    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"data\": {\"data\":[[\"Russian Federation\",\"yes\"]]}}"  \
    http://mlflow-gateway.rtarf-ml.its-software-services.com/v2/gateway | jq

    {
        "predictions": [
            "no"
        ]
    }
    
    curl -X POST -H "Content-Type:application/json"                     \
    --data "{\"data\": {\"data\":[[\"Russian Federation\",\"no\"]]}}"  \
    http://127.0.0.1:5000/gateway | jq

    {
        "predictions": [
            "yes"
        ]
    }
    
    while true;do curl -X POST -H "Content-Type:application/json"                     \
    --data '{"country": "Russian Federation","timestamp": "2023-05-13T13:45:34Z"}'  \
    http://127.0.0.1:6789/v2/gateway;done

## Docker Run

    docker run --name mlflow-api -p 6543:5000 -e MODEL_URI=gs://mlflow_gke_test_20230314/5/8911fc4e3a514e969cac16d157b008ed/artifacts/model -e SERVING_PORT=5000 -e GOOGLE_APPLICATION_CREDENTIALS="/data/app/secret/gcp.json" -v /mnt/d/firework/gcr-authen-json/gcp-dmp-devops.json:/data/app/secret/gcp.json mlflow_serving:v1

## Docker Rum into container

    docker run -it --entrypoint bash --name mlflow-api -p 6543:5000 -e MODEL_URI=gs://mlflow_gke_test_20230314/5/8911fc4e3a514e969cac16d157b008ed/artifacts/model -e SERVING_PORT=5000 -e GOOGLE_APPLICATION_CREDENTIALS="/data/app/secret/gcp.json" -v /mnt/d/firework/gcr-authen-json/gcp-dmp-devops.json:/data/app/secret/gcp.json mlflow_serving:v1