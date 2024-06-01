import weaviate

client = weaviate.connect_to_local()  # Connect with default parameters

try:
    print(client.is_ready())
    classObj = {"class":"user","vectorizer":"none"}
    client.schema.create_class(classObj)

finally:
    client.close()  # Ensure the connection is closed
    

import requests
def embeddings(texts:List[str]):
    url = "https://api.edenai.run/v2/text/embeddings"

    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "texts": texts,
        "providers": "google"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiY2RkY2E0YTYtM2ZiNS00NzJhLTkwMzgtNjEwNTdjYzlkYmRiIiwidHlwZSI6ImFwaV90b2tlbiJ9.PnOSsYKw7mmmkpbbFSScaxyaKw_q-5TkykDysJoCMtw"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    return response.json()


documents = [
    "Connect me with professionals in the field of artificial intelligence and machine learning.",
    "Find users who share my interest in hiking and outdoor adventures.",
    "Discover mentorship opportunities in software development for beginners.",
    "Explore upcoming tech events and meetups in San Francisco.",
    "Recommend books on entrepreneurship and startup strategies.",
    "Seek advice on transitioning from academia to industry in the field of biotechnology.",
    "Connect me with individuals passionate about environmental sustainability.",
    "Explore discussions on the latest advancements in renewable energy technology.",
    "Find language exchange partners for practicing Spanish conversation.",
    "Get feedback on my portfolio website design from fellow designers."
]