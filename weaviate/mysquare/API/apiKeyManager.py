from google.cloud.secretmanager import *
class ApiKeyManager():
    apiKey = ""
    def __init__(self, apiKey):
        self.apiKey = apiKey
    def isKeyValid(self):
        self.apiKey
        return True
    def uploadKey(self):
        secretManager = SecretManagerServiceClient().get_secret()
        return
    
#those are the commands for installation of google-cloud-secret-manager
'''
python3 -m venv <your-env>
source <your-env>/bin/activate
pip install google-cloud-secret-manager
'''
#https://cloud.google.com/python/docs/reference/secretmanager/latest/summary_method