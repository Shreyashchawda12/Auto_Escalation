import os
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

# Read Mongo URI and DB name from secrets or env
if "MONGO_URI" in st.secrets:
    MONGO_URI = st.secrets["MONGO_URI"]
    MONGO_DB = st.secrets["MONGO_DB"]
else:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "TELCOM_AI")

# Connect
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]  # explicitly define DB


# Insert alarms
def insert_bulk_alarms(records, collection_name):
    """Insert multiple alarms into MongoDB and return count only."""
    if not records:
        return 0
    collection = db[collection_name]
    result = collection.insert_many(records)
    return len(result.inserted_ids)   # ✅ return just the count


# Get open alarms
def get_open_alarms(collection_name):
    """Fetch alarms with EsclationStatus OPEN."""
    collection = db[collection_name]
    return list(collection.find({"EsclationStatus": "OPEN"}))
