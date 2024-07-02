from google.cloud import firestore
class firebase_helper():
    def __init__(self):
        self.db = firestore.Client(
            project=None,
            credentials=None,
            database=None
        )
    def upload_user(self, email, uuid, name, apiKey_encrypted):
        self.db.collection("users").add({"uuid":uuid,"email":email, "name":name, "apiKey":apiKey_encrypted})
    def upload_firstKey(self, email, apiKey):
        self.db.collection("clear_api_keys").add({"user":email, "apiKey":apiKey})
    def updateHistory(self, people:list[str], email):
        doc = self.db.collection("users").where("email", "==", email).limit(1).get()
        self.db.collection("users").document(doc[0].id).update({"people_search":doc[0].to_dict()["people_search"]+people})

'''
    RULES/BOZZA:
    WARNING: the firebase rules will be the following:
        IF user is authenticated the user can only write in his document (not premiumUser and apiKey those are READONLY), 
            can read everyone else BUT he cannot read everybody else apiKey
        ELSE IF THE BACKEND is god and can access/read/write anywhere
    IN ADDITION:
        The clear_api_keys collection will be clear (only the database can access that) and through the encrypted key will be verified
'''
    