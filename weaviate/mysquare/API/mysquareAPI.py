from fastapi import FastAPI, Query
from mangum import Mangum
import weaviate
import weaviate.classes.config as wvcc
import json
from promptTemplates import system_template, filter_prompt
import google.generativeai as genai
from dotenv import load_dotenv
import os
from helpers.apiKeyManager import ApiKeyManager, generateApiKey
import uvicorn
from weaviate.classes.query import MetadataQuery
from helpers.firebase_helper import firebase_helper

app = FastAPI()
handler = Mangum(app)

@app.get("/get_people/") #TODO add A LOT OF try/catch
async def getPeople(prompt: str = Query(None, description="prompt for searching people similar to you"), apikey:str = Query(None)):
    # Security.is_banned_IP(metaData["ip"])
    # Security.auth_user_key(metaData["userkey"]) #get api key, the apikey will be banned or not, and indicates the type, if user or not, and the premium or basic plan
    #substitute with key analizer
    analyzer = ApiKeyManager(apiKey=apikey)
    if(not analyzer.isKeyValid()):
        return json.encoder.JSONEncoder().encode(
            {
                "error": "Api key Invalid",
            }
        )
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"error":"error server response"})
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    llm = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    genai.GenerationConfig(max_output_tokens=1000, response_mime_type="application/json") #change with apikey setter, new class called configmodel
    embedder = genai.get_model("models/text-embedding-004")
    botResponse = llm.generate_content(system_template+"request:"+prompt)
    botJsonRaw = botResponse.text.replace("json","",1).replace("'","").replace("\n","").replace("```","").replace("'","")
    botJSON = json.loads(botJsonRaw)
    if(botJSON["validRequest"]):
        vector = genai.embed_content(
            model=embedder,
            content=botJSON["optimizedPrompt"], 
        )["embedding"]
        collection = client.collections.get("users")
        vector_response = collection.query.near_vector(
            near_vector=vector, # your query vector goes here
            limit=6, #include and delete the user itself
            return_metadata= MetadataQuery(distance=True,score=True,certainty=True)
        )
        return json.encoder.JSONEncoder().encode(
            {   #TODO add user id (from firebase id documents)
                "users":str([
                    {
                        "uuid": x.uuid,
                        "user": str(x.properties.get("name")),
                        "job_title": str(x.properties.get("job_title")),
                        "profile_img": str(x.properties.get("profile_img")),
                        "description": str(x.properties.get("description")),
                        "premiumUser": str(x.properties.get("premiumUser")),
                        "interests": str(x.properties.get("interests")),
                        "links": str(x.properties.get("links")),
                        "score": str(x.metadata.certainty)
                        } 
                    for x in vector_response.objects]),
                "error": "null",
                "bot_response": botJSON
            }
        )
    return json.encoder.JSONEncoder().encode(
            {
                "users":"null",
                "error": "content blocked, reason: prompt contains content filtered",
                "bot_response": botJSON
            }
        )
    
    
    
@app.post("/delete_user/")
async def delete_user(uuid:str=Query(None), apiKey:str=Query(None), secret_id:str= Query(None)):
    analyzer = ApiKeyManager(apiKey=apiKey, secret_id=secret_id)
    if(not analyzer.isKeyValid()):
        return json.encoder.JSONEncoder().encode(
                {
                    "error": "Api Key invalid",
                }
            )
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"error":"error server response"})
    collection = client.collections.get("users")
    success = collection.data.delete_by_id(uuid)
    if(success):
        result = {"error":"null", "SUCCESS":"true", "sad": "false :)"}
    else:
        result = {"error":"error deleting reference id", "SUCCESS": "false", "sad":"true :("}
    return json.encoder.JSONEncoder().encode(result)
    



@app.post("/upload_user/") #TODO this will be implemented in the client and then it will be invoked ONLY if the user has done the authentication
async def upload_user(name:str = Query(None), description:str = Query(None), email:str = Query(None)): #Manage in secret manager
    firebase_help = firebase_helper()
    ##########TODO manage errors better
    try:
        apiKey = generateApiKey()
        keyManager = ApiKeyManager(apiKey=apiKey)
        encryptedKey = keyManager.encryptedKey()
        firebase_help.upload_firstKey(email=email, apiKey=encryptedKey) #TODO uncomment
    except:
        return ({"error":"error authentication user key"})
    client = await weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"error":"error server response"})
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    embedder = genai.get_model("models/text-embedding-004")
    vector = genai.embed_content(
        model=embedder,
        content=description, 
    )["embedding"]
    collection = client.collections.get("users")
    try:
        uuid = collection.data.insert(
                properties={
                    "name": name,
                    "description": description,
                    "profileImg":"",
                    "email": email,
                    "jobTitle": "",
                    "premiumUser":False,
                    "interests":[],
                    "links":[]
                },
                vector=vector
        )
        firebase_help.upload_user(email=email, uuid=uuid, apiKey_encrypted=encryptedKey)
        return json.encoder.JSONEncoder().encode(
            {
                "SUCCESS": "request successful",
                "vector": str(vector[0:10])+"...",
                "apiKey": apiKey, #TODO ADD LOGIN SECURE FUNCTION, add client apikeyloginRetrievalError and local store
                "uuid":uuid
            }
        )
    except:
        return json.encoder.JSONEncoder().encode(
            {
                "error": "error uploading user",
            }
        )
    # return json.encoder.JSONEncoder().encode(
    #             {
    #                 "error": "content blocked, reason: prompt contains content filtered",
    #                 "botResponse":botJSON,
    #                 "isValid": botJSON["isValid"]
    #             }
    #         )
@app.get("/get_user/")
async def get_user(id:str = Query(None), apiKey:str = Query(None), secret_id:str = Query(None)):
    analyzer = ApiKeyManager(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        return json.encoder.JSONEncoder().encode(
                {
                    "error": "Api Key invalid",
                }
            )
    client = weaviate.connect_to_local()
    collection = client.collections.get("users")
    user_data = collection.query.fetch_object_by_id(id)
    return json.encoder.JSONEncoder().encode(
                {   
                    "propreties": user_data.properties,
                }
            )
        

@app.get("/test/")
async def test(name:str = Query(None)):
    return json.encoder.JSONEncoder().encode(
                {
                    "Greetings": "Hello my man!! Hello "+name,
                }
            )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)