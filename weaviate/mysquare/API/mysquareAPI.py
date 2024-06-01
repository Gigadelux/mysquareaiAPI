from fastapi import FastAPI, Query
from mangum import Mangum
import weaviate
import weaviate.classes.config as wvcc
import json
from promptTemplates import system_template, filter_prompt
import google.generativeai as genai
from dotenv import load_dotenv
import os
from apiKeyAnalyzer import ApiKeyAnalyzer
import uvicorn
from weaviate.classes.query import MetadataQuery

app = FastAPI()
handler = Mangum(app)

@app.get("/get_people/") #TODO add A LOT OF try/catch
async def getPeople(prompt: str = Query(None, description="prompt for searching people similar to you"), apikey:str = Query(None)):
    # Security.is_banned_IP(metaData["ip"])
    # Security.auth_user_key(metaData["userkey"]) #get api key, the apikey will be banned or not, and indicates the type, if user or not, and the premium or basic plan
    #substitute with key analizer
    analyzer = ApiKeyAnalyzer(apiKey=apikey)
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
            {
                "users":str([{"uuid": x.uuid, "user": str(x.properties.get("name")), "description": str(x.properties.get("description")), "score": str(x.metadata.certainty)} for x in vector_response.objects]),
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
async def delete_user(uuid:str=Query(None), apiKey:str=Query(None)):
    analyzer = ApiKeyAnalyzer(apiKey=apiKey)
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
    



@app.post("/upload_user/")
async def upload_user(name:str = Query(None), description:str = Query(None), apiKey:str = Query(None)):
    analyzer = ApiKeyAnalyzer(apiKey=apiKey)
    if(not analyzer.isKeyValid()):
        return json.encoder.JSONEncoder().encode(
                {
                    "error": "Api Key invalid",
                }
            )
    client = weaviate.connect_to_local()  # Connect with default parameters
    if(not client.is_ready()):
        return str({"error":"error server response"})
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    llm = genai.GenerativeModel(model_name="models/gemini-1.0-pro")
    genai.GenerationConfig(max_output_tokens=100, response_mime_type="application/json") #change with apikey setter, new class called configmodel
    embedder = genai.get_model("models/text-embedding-004")
    botResponse = llm.generate_content(filter_prompt+" User{"+name+description+"}")
    botJsonRaw = botResponse.text.replace("json","",1).replace("'","").replace("\n","").replace("```","").replace("'","")
    botJSON = json.loads(botJsonRaw)
    if(True): #TODO fix this
        vector = genai.embed_content(
            model=embedder,
            content=description, 
        )["embedding"]
        collection = client.collections.get("users")
        try:
            uuid = collection.data.insert(
                    properties={
                        "name": name,
                        "description": description
                    },
                    vector=vector
            )
            return json.encoder.JSONEncoder().encode(
                {
                    "SUCCESS": "request successful",
                    "vector": str(vector[0:10])+"...",
                    "botjson" : json.encoder.JSONEncoder().encode(botJSON)
                }
            )
        except:
            return json.encoder.JSONEncoder().encode(
                {
                    "error": "error uploading user",
                }
            )
    return json.encoder.JSONEncoder().encode(
                {
                    "error": "content blocked, reason: prompt contains content filtered",
                    "botResponse":botJSON,
                    "isValid": botJSON["isValid"]
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