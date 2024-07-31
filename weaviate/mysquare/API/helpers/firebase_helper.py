from google.cloud import firestore
class firebase_helper():#TODO make a function that checks if the uuid of user is not null for login function in the api in case of errors
    def __init__(self):
        self.db = firestore.Client(
            project=None,
            credentials=None,
            database=None
        )
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
    