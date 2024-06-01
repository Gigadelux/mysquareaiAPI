from fastapi import FastAPI, Query
from mangum import Mangum
import weaviate
import weaviate.classes.config as wvcc

from embedder import embedder
from searchEngine import searchEngine
from userUpdater import userUpdater
from security import Security
import json

app = FastAPI()
handler = Mangum(app)

@app.get("/get_people/")
async def getPeople(prompt: str = Query(None, description="prompt for searching people similar to you"), metaData:str = Query(None, "")):
    Security.is_banned_IP(metaData["ip"])
    Security.auth_user_key(metaData["userkey"])
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"errorcode":"504"})
    embedded_prompt = embedder.embed(prompt)
    SE = searchEngine(client)
    people = SE.search_people(embedded_prompt, metaData["username"])
    vector_id = SE.upload_vector(query_vector=embedded_prompt,raw_query=prompt)
    try:
        return str({"result":people, "vector_id": vector_id, "query_vector":embedded_prompt}) #client will upload the result on vector_id history on firebase
    except:
        return str({"errorcode":"404"})
    
@app.post("/update_user_behavior/")
async def update_user_behavior(credentials:str = Query(None, ""), data_to_upload:str = Query(None, "")):
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"errorcode":"504"})
    cred = json.loads(credentials)
    data = json.loads(data_to_upload)
    userConnection = userUpdater(cred)
    userConnection.connect_to_firebase()
    userConnection.updateBehavior(client, data["query_vector"],0.5)
    userConnection.updateHistory(data_to_upload["uuid"])
    return str({"Success": "true"})


@app.get("/get_topics/")
async def get_topics(data:str = Query(None, "")):
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"errorcode":"504"})
    SE = searchEngine(client=client)
    result = SE.get_topics(data["query_vector"])
    return str(result)