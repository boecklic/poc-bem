import requests
import json

class ApiGatewayResponse():

    def __init__(self, payload, status=200, headers={}):
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.headers.update(headers)

        self.status = status
        self.payload = payload

    def json(self):
        return {
            'statusCode': self.status,
            'headers': self.headers,
            'body': json.dumps(self.payload)
        }

def handle(event, context):
    response = requests.get("https://ltboc.infra.bgdi.ch/layerservice/api/v4/datasets")
    payload = response.json()
    # payload['x-lambda-hello'] = "Hello World!"

    new_payload = {}
    for dataset in payload['results']:
        metadata = dataset.get('metadata', {})
        new_payload[dataset['name']] = {
            'serverLayerName': dataset['name'],
            'chargeable': dataset['chargeable'],
            'attributionUrl': metadata.get('url_portal','')
        }

    return ApiGatewayResponse(payload=new_payload).json()