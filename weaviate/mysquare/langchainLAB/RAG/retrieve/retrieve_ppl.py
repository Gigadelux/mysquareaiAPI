from langchain.tools import BaseTool
import google.generativeai as genai 
from dotenv import load_dotenv
import os
import weaviate
import weaviate.collections.config as wvcc

class Retrieve_people_tool():
    name = "Get Webpage"
    description = "Useful for when you need to get the content from a specific webpage"

    def _run(self, prompt: str):
        load_dotenv("../")
        GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
        genai.configure(GOOGLE_API_KEY)
        embedder = genai.get_model("models/text-embedding-004")
        vector = genai.embed_content(
            model=embedder,
            content=prompt,
        )
        client = weaviate.connect_to_local()
        collection = client.collections.get("metadata")
        response = collection.query.near_vector(
            near_vector=vector, # your query vector goes here
            limit=6, #include and delete the user itself
            return_metadata=wvcc.query.MetadataQuery(distance=True)
        )
        return response
