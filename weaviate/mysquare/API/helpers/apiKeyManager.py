from google.cloud.secretmanager import *
from google.auth import credentials
from dotenv import load_dotenv
import os
import time
import random
import string
from helpers.secretManagerService_helper import SecretManagerService_Helper
from helpers.firebase_helper import firebase_helper
from cryptography.fernet import Fernet
'''!IMPORTANT to manage the keys and verify them I will put only the encryption key in the secretManager, and it will change from user email'''
class ApiKeyManager():
    apiKey = ""
    def __init__(self, apiKey):#add project_id and secret_id
        self.apiKey = apiKey
    def isKeyValid(self):
        self.apiKey
        return True
    def uploadKey(self, email):
        firebase_helper().upload_firstKey(email=email, apiKey=self.apiKey)
    def encryptedKey(self)->str:
        load_dotenv()
        secret_id = os.getenv("APIS_ENCRYPTION_KEY")
        payload = SecretManagerService_Helper().access_secret_version()
        fernet = Fernet(key=payload.encode())
        encryptedKey = fernet.encrypt(self.apiKey)
        return encryptedKey.decode()
    def get(self):
        return self.apiKey
    
        
    
#those are the commands for installation of google-cloud-secret-manager
'''
python3 -m venv <your-env>
source <your-env>/bin/activate
pip install google-cloud-secret-manager
'''
#https://cloud.google.com/python/docs/reference/secretmanager/latest/summary_method

def generateApiKey()->str:
     # Get the current timestamp down to the millisecond
    timestamp = int(time.time() * 1000)
    
    # Append a random letter to the timestamp
    random_letter = random.choice(string.ascii_letters)
    combined_string = f"{timestamp}{random_letter}"
    
    # Transform the resulting string into a base36 representation
    base36_characters = string.digits + string.ascii_lowercase
    base36_string = ""
    num = int.from_bytes(combined_string.encode(), 'big')
    
    while num:
        num, i = divmod(num, 36)
        base36_string = base36_characters[i] + base36_string
    char_list = list(base36_string)
    
    # Shuffle the list of characters
    random.shuffle(char_list)
    
    # Join the shuffled characters back into a string
    shuffled_string = ''.join(char_list)
    while len(shuffled_string) < 65:
        shuffled_string += random.choice(string.ascii_letters + string.digits)
    return shuffled_string