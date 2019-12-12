from flask import Flask, escape, request, make_response
from flask_cors import CORS
import json
import requests
from py_execution import main

app = Flask(__name__)
CORS(app, resources=r'/*')


@app.route('/', methods=["GET", "POST"])
def hello():
    if (request.method == "POST"):

        bodyData = request.get_json()
        dataForTool = []

        for data in bodyData[1:]:
            if type(data) == str:
                dataFromApi = requests.get(data).json()
                dataForTool.append(dataFromApi)
            else:
                dataForTool.append(data)

        if bodyData[0] == "Main":

            json_data_0 = json.dumps(dataForTool[0])
            json_data_1 = json.dumps(dataForTool[1])

            result = json.loads(main("LC", [json_data_0, json_data_1]))
            resultDataId = requests.post("https://cache.rrworkflow.com/putData", json=result).text
            resultSend = json.dumps(["https://cache.rrworkflow.com/getData?" + resultDataId])
            response = make_response(resultSend)


    elif (request.method == "GET"):
        apiInfo = {
            "name": "Lu Chen",
            "desc": "Lu Chen's script",
            "methods": [
                {
                    "name": "Main",
                    "parameter": ["example", "industry+list"],
                    "output": ["Result"]
                }
            ]
        }
        response = make_response(json.dumps(apiInfo))

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response
