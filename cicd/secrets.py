import json
import boto3


class Secrets:
    def __init__(self):
        self._s3 = boto3.client('s3', region_name='us-east-1')

    def slack_app_token(self):
        obj = self._s3.get_object(Bucket='sensibo-secrets', Key='slack.json')
        return json.loads(obj['Body'].read().decode())['slack-app-SensiboCI-token']
