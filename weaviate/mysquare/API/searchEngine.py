
import weaviate
import weaviate.classes as wvcc

from userUpdater import userUpdater
class searchEngine:
    def __init__(self, client):
        self.client = client
        
    def search_people(self,client:weaviate.WeaviateClient,query_vector:list, username:str):
        user_behaviors = client.collections.get("Users_behave")
        try:
            return _indexing_query(user_behaviors, query_vector,0, username)
        except:
            return [{"error":"maintance error"}]
    
    def get_topics(self, query_vector:list):
        topics = self.client.collections.get("Topics")
        return _indexing_query(topics, query_vector,1)
    
    def upload_vector(self, raw_query:str, query_vector:list):
        collection = self.client.collections.get("queries")
        uuid = collection.data.insert(
            properties={
                "query": raw_query
            },
            vector=query_vector
        )
        return uuid
        #userUpdater.insert_object(uuid)
    
    
 
def _indexing_query(collection, query_vector:list,operation_type:int, username=None):
    if(operation_type==1 and username is None):
        raise Exception("request requires username but is None")
    response = collection.query.near_vector(
        near_vector=query_vector, # your query vector goes here
        limit=11, #include and delete the user itself
        return_metadata=wvcc.query.MetadataQuery(distance=True)
    )
    results = []
    for o in response.objects:
        if(operation_type==0):
            if(username != o.properties["username"]):
                results.append({"username":o.properties["username"], "distance":o.metadata.distance})
        else:
            results.append({"topic":o.properties["topic"]})
    return results