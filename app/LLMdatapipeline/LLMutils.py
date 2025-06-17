"""
LLM-utils.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ utility functions for LLM ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""
import json

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import time
import torch

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="qdrant", port=6333)

def setup_qdrant():
    #called as function to wait for docker to setup fastapi
    for attempt in range(5):
        try:
            collections = client.get_collections().collections
            break
        except Exception as e:
            print("waiting for Qdrant ...")
            time.sleep(2)
    else:
        raise RuntimeError("Qdrant didnt start")
        
    if "hikes" not in [col.name for col in collections]:
        client.recreate_collection(
            collection_name="hikes",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

#----------------------------------[summarize tool]----------------------------------
MAX_SUMMARY_LENGTH = 100
MIN_SUMMARY_LENGTH = 30

summarizer = pipeline("summarization", model="t5-small")

def summarize(text):
    return summarizer(text, max_length=MAX_SUMMARY_LENGTH, min_length=MIN_SUMMARY_LENGTH, do_sample=False)[0]["summary_text"]

#----------------------------------[ Embed data]----------------------------------
"""
Embeds provided data with numerical representation vector based off description 

How it works: 
    It takes in the data saved in collected_data.json, summarizes the copied hike description to be able
    to use less tokens to process the sumamry, and then upserts it to Qdrant for storage and faster access

"""

def embed_data():
    with open("collected_data.json","r") as file:
        data = file.read()
        hikes = json.loads(data)

        for i, hike in enumerate(hikes):
            id = i+1
            
            trail_name = hike["Trail name"]
            trail_distance = hike["Length"]
            trail_time = hike["Estimated time"]
            trail_description = summarize(hike["Summary"])

            trail_string = f"{trail_name} is a {trail_distance} hike that takes around {trail_time} to complete. {trail_description}"
            vector = model.encode(trail_string).tolist()
            client.upsert(
                collection_name="hikes",
                points=[
                    PointStruct(
                        id=id,
                        vector=vector,
                        payload={
                            "hike_name": trail_name,
                            "distance": trail_distance,
                            "time_to_complete": trail_time,
                            "summary": trail_description
                        }
                    )
                ]
            )

        