from fastapi import FastAPI, HTTPException, Query
from mangum import Mangum
from pydantic import BaseModel
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
from firebase_admin import auth, credentials, initialize_app
import firebase_admin
import numpy as np
from cryptography.fernet import Fernet
##TODO mettere un limite alle chiamate giornaliere nella versione premium e in quella normale (evitare l'abuso in caso di attacco)
#TODO sobstitute {error} with HTTPEXCEPTION
#TODO use multimodal embedder for premium and other calls.
app = FastAPI()
handler = Mangum(app)

@app.get("/get_people/") #TODO add A LOT OF try/catch
async def getPeople(prompt: str = Query(None, description="prompt for searching people similar to you"), apikey:str = Query(None)):
    # Security.is_banned_IP(metaData["ip"])
    # Security.auth_user_key(metaData["userkey"]) #get api key, the apikey will be banned or not, and indicates the type, if user or not, and the premium or basic plan
    #substitute with key analizer
    analyzer = ApiKeyManager(apiKey=apikey)
    if(not analyzer.isKeyValid()):
        raise HTTPException(401, detail="Error key not valid")
    load_dotenv()
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    client = weaviate.connect_to_wcs(
        cluster_url=URL,
        auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    if(not client.is_ready()):
        raise HTTPException(500, detail="Internal error")
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
        vector_response = collection.query.hybrid(
            alpha=0.25,
            query=botJSON["optimizedPrompt"],
            vector=vector, # your query vector goes here
            limit=6, #include and delete the user itself
            return_metadata= MetadataQuery(distance=True,score=True,certainty=True),
        )
        #TODO update history here
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
                "bot_response": botJSON,
            }
        )
    raise HTTPException(401, detail="prompt filtered")
    
    
    
@app.post("/delete_user/")
async def delete_user(uuid:str=Query(None), apiKey:str=Query(None)):
    analyzer = ApiKeyManager(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        raise HTTPException(401, detail="Error key not valid")
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    client = weaviate.connect_to_wcs(
        cluster_url=URL,
        auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    if(not client.is_ready()):
        raise HTTPException(500, detail="Internal server error")
    collection = client.collections.get("users")
    success = collection.data.delete_by_id(uuid)
    if(success):
        result = {"error":"null", "SUCCESS":True, "sad": "false :)"} #wtf TODO delete
    else:
        raise HTTPException(500, detail="Internal server error")
    return json.encoder.JSONEncoder().encode(result)
    



@app.post("/upload_user/") #TODO this will be implemented in the client and then it will be invoked ONLY if the user has done the authentication
async def upload_user(name:str = Query(None), description:str = Query(None), email:str = Query(None)): # password:str = Query(None) Manage in secret manager
    firebase_help = firebase_helper()
    ##########TODO manage errors better
    try:
        apiKey = generateApiKey()
        keyManager = ApiKeyManager(apiKey=apiKey)
        deckey = Fernet.generate_key()
        text_deckey = deckey.decode()
        encryptedKey = keyManager.encryptedKey(text_deckey)
        firebase_help.upload_firstKey(email=email, apiKey=apiKey, decriptionKey=text_deckey) #TODO uncomment
    except Exception as e:
        print(e)
        raise HTTPException(401, detail="Error key not valid")
    #TODO verify user email password here:
    try:
        userFound = firebase_help.check_user_exists(email=email)
        # if(not userFound):
        #    raise HTTPException(404) #TODO uncomment after debug
    except Exception as e:
        print(str(e))
        raise HTTPException(401, detail="User need to login first")
    userRegistered = firebase_help.user_subscribed(email=email)
    # if(userRegistered):
    #    raise HTTPException(401, detail="User already subscribed") #TODO uncomment after debug
    load_dotenv()
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    client = weaviate.connect_to_wcs(
        cluster_url=URL,
        auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    if(not client.is_ready()):
        raise HTTPException(500, detail="Weaviate not initialized")
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
        firebase_help.upload_user(name=name, email=email, uuid=str(uuid), apiKey_encrypted=encryptedKey)
        return json.encoder.JSONEncoder().encode(
            {
                "SUCCESS": True,
                "vector": str(vector[0:10])+"...",
                "apiKey": apiKey, #TODO ADD LOGIN SECURE FUNCTION, add client apikeyloginRetrievalError and local store 
                #TODO delete apikey returnfor security reason (obv motherfucker)
                "uuid":uuid
            }
        )
    except Exception as e:
        print(e)
        raise HTTPException(500, detail="error inserting vector")
    # return json.encoder.JSONEncoder().encode(
    #             {
    #                 "error": "content blocked, reason: prompt contains content filtered",
    #                 "botResponse":botJSON,
    #                 "isValid": botJSON["isValid"]
    #             }
    #         )
@app.get("/get_user/")
async def get_user(id:str = Query(None), apiKey:str = Query(None)):
    analyzer = ApiKeyManager(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        raise HTTPException(401, detail="api key invalid")
    load_dotenv()
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    try:
        client = weaviate.connect_to_wcs(
            cluster_url=URL,
            auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    except:
        HTTPException(500, detail="Internal server error")
    collection = client.collections.get("users")
    try:
        user_data = collection.query.fetch_object_by_id(id)
    except:
        raise HTTPException(404, detail="user not found")
    return json.encoder.JSONEncoder().encode(
                {   
                    "propreties": user_data.properties,
                }
            )
        
    
@app.post("/update_user/")
async def update_user(id:str = Query(), apiKey:str = Query(), description:str = Query()):
    #firebase = firebase_helper()
    #TODO here firebase updating
    #TODO here weaviate.insert updating
    analyzer = ApiKeyManager(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        raise HTTPException(401, detail="api key invalid")
    load_dotenv()
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    try:
        client = weaviate.connect_to_wcs(
            cluster_url=URL,
            auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    except:
        HTTPException(500, detail="Internal server error")
    if(len(description)!=0):
        wcs_doc = client.collections.get("users").data.update( #TODO check null or empty paramethers in data
            uuid=id,
            properties={
                "description":description,
            }
        )
        return {"id": id,"updating_status":200}
    else:
        raise HTTPException(406, detail="argument description is empty")

@app.post("/update_interests/")
async def update_interests(id:str = Query(), apiKey:str = Query(), interests:list = Query()):
    #firebase = firebase_helper()
    #TODO here firebase updating
    #TODO here weaviate.insert updating
    analyzer = ApiKeyManager(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        raise HTTPException(401, detail="api key invalid")
    load_dotenv()
    # Set these environment variables
    URL = os.getenv("WCS_URL")
    WCSAPIKEY = os.getenv("WCS_API_KEY")
    # Connect to a WCS instance
    try:
        client = weaviate.connect_to_wcs(
            cluster_url=URL,
            auth_credentials=weaviate.auth.AuthApiKey(WCSAPIKEY))
    except:
        HTTPException(500, detail="Internal server error")
    collection = client.collections.get("users")
    try:
        user_data = collection.query.fetch_object_by_id(id)
    except:
        raise HTTPException(404, detail="user not found")
    oldInterests = user_data.properties["interests"]
    if(len(oldInterests)!=0):
        def differences(l1, l2): #TODO maybe is better to add the new interests vector alone?
            added = []
            subtracted = []
            for i in l1:
                if(not l2.contains(i)):
                    subtracted.append(i)
            for j in l2:
                if(not l1.contains(i)):
                    added.append(j)
            return {"added": added, "subtracted": subtracted}
        diff = differences(oldInterests, interests)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        embedder = genai.get_model("models/text-embedding-004")
        vectorAdded = genai.embed_content(
            model=embedder,
            content=str(diff["added"]), 
        )["embedding"]
        vectorSubtracted = genai.embed_content(
            model=embedder,
            content=str(diff["subtracted"]), 
        )["embedding"]
        vAdd = np.array(vectorAdded)
        vSub = np.array(vectorSubtracted)
        oldVec = np.array(user_data.vector["default"])
        newVec = oldVec + vAdd - vSub
        collection.data.update(
            uuid=id,
            vector= newVec.tolist()
        )
        return {"id": id,"updating_status":200}
    else:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        embedder = genai.get_model("models/text-embedding-004")
        vectorAdded = genai.embed_content(
            model=embedder,
            content=str(interests), 
        )["embedding"]
        vAdd = np.array(vectorAdded)
        oldVec = np.array(user_data.vector["default"])
        newVec = oldVec + vAdd
        collection.data.update(
            uuid=id,
            vector= newVec.tolist()
        )
        return {"id": id,"updating_status":200}

@app.get("/test/")
async def test(name:str = Query(None)):
    try:
        return {"Greetings": "Hello my man!! Hello "+name}
    except:
        return {"Greetings":"I'm so sad you did not tell me ur name"}

#FIREBASE TODO more fuckin elegant!!!!!! NOT MONOLITIC ECHECAZZO
'''
ATTENZIONE!!!!!!!!!!! 
nel client la fottuta registrazione sarà in contemporanea tra 
l'autenticazione su firebase e l'autenticazione per l'upload utente 
al momento della registrazione.
in caso di errore SI FA IL LOGOUT DAL CLIENT
'''
    
class UserCredentials(BaseModel):
    email: str
    password: str

# Endpoint to verify user credentials
@app.get("/verify_user/")
async def verify_user_credentials(credentials: UserCredentials):
    try:
        # Verify user credentials using Firebase Authentication
        user = auth.get_user_by_email(credentials.email)
        cred = credentials.Certificate('path/to/serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
        # Sign in with email and password to verify credentials
        auth.verify_password(credentials.email, credentials.password)
        
        # If no exception is thrown, credentials are valid
        return {"message": "Credentials verified successfully", "status": True}
    
    except auth.AuthError as e:
        # Handle authentication errors (e.g., invalid credentials)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    except firebase_admin.exceptions.FirebaseError as e:
        # Handle Firebase SDK errors
        raise HTTPException(status_code=500, detail="Firebase error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)