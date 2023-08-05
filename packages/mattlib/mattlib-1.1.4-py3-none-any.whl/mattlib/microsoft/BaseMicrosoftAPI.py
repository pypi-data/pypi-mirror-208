import sys
sys.path.append('../mattlib')
from mattlib.BaseAPI import BaseAPI
import requests
import os
import json
import pathlib

class BaseMicrosoftAPI(BaseAPI):
    required_info = [
        ("tenant_ID", "str"),
        ("app_ID", "str"),
        ("secret_key", "str")
    ]
    def connect(self, tenant_ID, app_ID, secret_key, scope):
        self.tenant_ID = tenant_ID.rstrip()
        self.app_ID = app_ID.rstrip()
        self.secret_key = secret_key.rstrip()
        self.scope = scope
        self.headers = self.get_auth()

    def get_auth(self):
        token_url = f'https://login.microsoftonline.com/'\
                    f'{self.tenant_ID}/oauth2/v2.0/token'
        auth = {
            'grant_type': 'client_credentials',
            'client_id': self.app_ID,
            'client_secret': self.secret_key,
            'scope': self.scope,
        }
        response = requests.post(token_url, data=auth)
        token = response.json().get('access_token')
        if token != None:
            headers = {'Authorization': f'Bearer {token}'}
            return headers
        else:
            raise Exception(f' BaseMicrosoftAPI authentication failed.\n'\
                            f'Response: {response}')

    def call_api_stream(self, url):
        response = requests.get(url, headers=self.headers)
        return response.text

    def call_api(self, url):
        values = []
        while url != None:
            response = requests.get(url, headers=self.headers)
            status = response.status_code
            if status != 200:
#                print('Response error')
#                print(response.text)
                return None
            response = json.loads(response.text)
            values += response['value']
            if 'nextLink' in response.keys():
                url = response['nextLink']
            if '@odata.nextLink' in response.keys():
                url = response['@odata.nextLink']
            else :
                url = None
        return values
