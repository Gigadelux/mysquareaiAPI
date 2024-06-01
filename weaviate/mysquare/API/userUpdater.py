import weaviate
import weaviate.classes.config as wvcc
import numpy as np
from searchEngine import searchEngine
import google.cloud.firestore_admin_v1 as firestore
class userUpdater:
    def __init__(self, credentials:dict):
        self.credentials = None
        #self.id = GETTER.get_id(credentials)
        self.FIREBASE_INSTANCE = None
    
    def connect_to_firebase(self):
        pass
    
    def get_user_vector(self):
        pass    
    
    def updateBehavior(self,client:weaviate.WeaviateClient,newQuery:list, learning_rate): #''', properties_query'''):
        try:
            # Convert lists to numpy arrays if they aren't already
            users_behavior = client.collections.get("Users_behave")
            userPosition = users_behavior.query.fetch_object_by_id(self.get_user_vector())
            userPosition = userPosition.vector["default"]

            # Apply the basic vector update formula
            updated_user_vector = self.move_vector(userPosition, newQuery, learning_rate)
            #Update to the weaviateClient and firebase
            users_behavior.data.update(
                uuid=self.id,
                properties={"username": self.credentials["username"]},
                vector=updated_user_vector.tolist()
            )
            self.updateTopics(newQuery)
            return True
        except:
            return False
    
    def updateTopics(self, newQuery:list):
        searchEngine.get_topics(newQuery)
        #topic manipulation
        pass
    
    def upload_vector_objects(self, objects:list):
        pass
    
    def updateHistory(self, uuid:str, email:str):
        
        pass

    def move_vector(self, old, new, alpha):
        
        user_vector = np.array(old)
        newQuery_vector = np.array(new)

        # Apply the basic vector update formula
        return user_vector + alpha * (newQuery_vector - user_vector)
    
    def uploadQuery(self,query:str):
        pass
    
    def insert_object(self, uuid):
        pass
