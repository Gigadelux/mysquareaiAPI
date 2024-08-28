from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials,auth
import os
from dotenv import load_dotenv
import json

class firebase_helper():#TODO make a function that checks if the uuid of user is not null for login function in the api in case of errors
    def __init__(self):
        load_dotenv()
        service_account_key = json.decoder.JSONDecoder().decode(os.getenv("GOOGLE_ADMIN_CREDENTIALS"))
        cred = credentials.Certificate(service_account_key)
        print(service_account_key)
        firebase_admin.initialize_app(cred)
        self.db = firestore.Client(credentials=cred)
    def docExist(self, docCollection,docName:str): #todo sono ubriaco da rifare
        try:
            
            # If user exists, retrieve their document from Firestore
            doc_ref = self.db.collection(docCollection).document(docName)
            doc_snapshot = doc_ref.get()
            
            if doc_snapshot.exists:
                return True
            else:
                return False
        except Exception as e:
            print(e) #TODO remove after debug
            return False
        

    def check_user_exists(self, email):
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
            return True # User exists
        except auth.UserNotFoundError:
            return False  # User does not exist
        except Exception as e:
            return False  # Other errors
    def upload_user(self, email, uuid, name, apiKey_encrypted): #TODO users sign up starts here
        self.db.collection("users").add({"uuid":uuid,"email":email, "name":name, "apiKey":apiKey_encrypted})
    def upload_firstKey(self, email, apiKey):
        self.db.collection("clear_api_keys").add({"user":email, "apiKey":apiKey})
    def updateHistory(self, prompt:str, id:str):
        self.db.collection("users").document(id).collection("history").add({"prompt":prompt, "dateTime": firestore.SERVER_TIMESTAMP})

'''
    RULES/BOZZA:
    WARNING: the firebase rules will be the following:
        IF user is authenticated the user can only write in his document (not premiumUser and apiKey those are READONLY), 
            can read everyone else BUT he cannot read everybody else apiKey
        ELSE IF THE BACKEND is god and can access/read/write anywhere
    IN ADDITION:
        The clear_api_keys collection will be clear (only the database can access that) and through the encrypted key will be verified
'''
