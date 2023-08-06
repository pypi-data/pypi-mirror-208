import requests
import base64

class authenticate:
    def __init__(self, base_url = 'http://0.0.0.0:4000'):
        self.base_url = base_url

    def authenticate(self, username, password):
        url = f'{self.base_url}/authenticate'
        credentials = f'{username}:{password}'.encode('ascii')
        encoded_credentials = base64.b64encode(credentials).decode('ascii')
        headers = {'Authorization': f'Basic {encoded_credentials}'}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('token_type')
        else:
            return None, None
