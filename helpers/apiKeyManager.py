import base64
from google.auth import credentials
from dotenv import load_dotenv
import os
import time
import random
import string
from helpers.firebase_helper import firebase_helper
from cryptography.fernet import Fernet
import hashlib
'''!IMPORTANT to manage the keys and verify them I will put only the encryption key in the secretManager, and it will change from user email'''
class ApiKeyManager():
    apiKey = ""
    def __init__(self, apiKey):#add project_id and secret_id
        self.apiKey = apiKey
    def isKeyValid(self):
        firebase_helper = firebase_helper()
        #TODO check on apikeys
        return True
    def uploadKey(self, email):
        firebase_helper().upload_firstKey(email=email, apiKey=self.apiKey)
    def encryptedKey(self, key_str)->str:
        hashed_key = hashlib.sha256(key_str.encode()).digest()
        # 2. Encode the hashed key to base64 to meet Fernet's key requirements
        key = base64.urlsafe_b64encode(hashed_key[:32])
        fernet = Fernet(key=key)
        encryptedKey = fernet.encrypt(self.apiKey.encode())
        print(encryptedKey.decode())
        return encryptedKey.decode()
    def decryptKey(self):
        load_dotenv()
        key = os.getenv("APIS_ENCRYPTION_KEY")
        fernet = Fernet(key=key.encode())
        return fernet.decrypt(self.apiKey).decode()
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