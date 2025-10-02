import os
from dotenv import load_dotenv

# Try importing Streamlit (only works if running inside Streamlit app)
try:
    import streamlit as st
    STREAMLIT = True
except ImportError:
    STREAMLIT = False

# Load .env when running locally
load_dotenv()

# -------------------------------
# MongoDB Settings
# -------------------------------
if STREAMLIT and "MONGO_URI" in st.secrets:
    MONGO_URI = st.secrets["MONGO_URI"]
    MONGO_DB = st.secrets["MONGO_DB"]
else:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "TELCOM_AI")

# -------------------------------
# Telegram Bot Settings
# -------------------------------
if STREAMLIT and "BOT_TOKEN" in st.secrets:
    BOT_TOKEN = st.secrets["BOT_TOKEN"]
    TEST_MODE = st.secrets.get("TEST_MODE", "True") == "True"
    TEST_CHAT_ID = st.secrets.get("TEST_CHAT_ID", "")
else:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    TEST_MODE = os.getenv("TEST_MODE", "True") == "True"
    TEST_CHAT_ID = os.getenv("TEST_CHAT_ID", "")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN missing! Please set it in .env or Streamlit secrets.toml")

# -------------------------------
# VNOC Login (optional for auto-download)
# -------------------------------
if STREAMLIT and "VNOC_USERNAME" in st.secrets:
    VNOC_USERNAME = st.secrets.get("VNOC_USERNAME", "")
    VNOC_PASSWORD = st.secrets.get("VNOC_PASSWORD", "")
else:
    VNOC_USERNAME = os.getenv("VNOC_USERNAME", "")
    VNOC_PASSWORD = os.getenv("VNOC_PASSWORD", "")

# -------------------------------
# File Paths
# -------------------------------
CLEANED_ALARM_FILE = "data/processed/cleaned_alarms.csv"
MAPPING_FILE = "data/mapping/site_escalation_mapping.xlsx"
