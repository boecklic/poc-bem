#!/usr/bin/env python
import json
import boto3
import botocore

PYTHON_3_6 = "python3.6"

PROJECT_NAME = 'poc-layerservice'

ROLE_NAME = f"{PROJECT_NAME}-LambdaBasicExecution"

# take credentials from ~/.aws/credentials
# select profile with profile_name
session = boto3.Session(profile_name='test1')

# @aws_lambda_async(capture_response=True)
# def longrunner(delay):
#     sleep(float(delay))
#     return {'MESSAGE': "It took {} seconds to generate this.".format(delay)}

# This Python snippet uses boto3 to create an IAM role named LambdaBasicExecution
 # with basic lambda execution permissions.
role_policy_document = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

iam_client = session.client('iam')

# check https://stackoverflow.com/a/49456606 on how
# to deal with exceptions
try:
    role = iam_client.get_role(RoleName=ROLE_NAME)
except iam_client.exceptions.NoSuchEntityException:
    iam_client.create_role(
      RoleName=ROLE_NAME,
      AssumeRolePolicyDocument=json.dumps(role_policy_document),
    )    


lambda_client = session.client('lambda')

env_variables = dict() # Environment Variables
with open('lambda_test/lambda.zip', 'rb') as fp:
    zipped_code = fp.read()


FUNCTION_NAME = f"{PROJECT_NAME}-handler"
try:
    lambda_client.get_function(
        FunctionName=FUNCTION_NAME
    )
except lambda_client.exceptions.ResourceNotFoundException:
    lambda_client.create_function(
      FunctionName=FUNCTION_NAME,
      Runtime=PYTHON_3_6,
      Role=role['Role']['Arn'],
      Handler='handler.handler',
      Code=dict(ZipFile=zipped_code),
      Timeout=300, # Maximum allowable timeout
      Environment=dict(Variables=env_variables),
    )

test_event = dict(plot_url="https://plot.ly/~chelsea_lyn/9008/")

res = lambda_client.invoke(
  FunctionName=FUNCTION_NAME,
  # InvocationType='Event',
  InvocationType='RequestResponse',
  Payload=json.dumps(test_event),
)
print(res)
res_payload = json.loads(res['Payload'].read())
print(res_payload)