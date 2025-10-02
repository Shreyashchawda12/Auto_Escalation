import os
import sys
import logging
import streamlit as st
import pandas as pd

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.preprocessor import load_and_preprocess_alarm_file
from telegram_bot.escalate_alarms import escalate_alarms   # ✅ updated
from mongodb.mongo_crud import insert_bulk_alarms
from automation.download_and_preprocess import get_latest_downloaded_file, clear_download_folder
from utils.mongo_utils import df_to_dicts

# Constants
DOWNLOAD_DIR = os.path.abspath("data/raw")
PROCESSED_OUTPUT = "data/processed/cleaned_alarms.csv"
COLLECTION_NAME = "AlarmLogs"

# UI
st.title("🚨 Alarm Automation Dashboard")

mode = st.radio("Choose Input Mode", ["🖐 Manual Download (VNOC)", "📤 Manual Upload"])

# --- Manual Upload ---
if mode == "📤 Manual Upload":
    uploaded_file = st.file_uploader("Upload Alarm Log File", type=["xlsx", "csv"])
    if uploaded_file is not None:
        uploaded_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)
        with open(uploaded_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"📂 Uploaded file saved: {uploaded_file.name}")
        source_file = uploaded_path
    else:
        source_file = None
else:
    # --- Manual Download Mode ---
    st.info("👉 Please manually download the alarm log file from VNOC into `data/raw` folder.")
    if st.button("🔄 Check for New File"):
        clear_download_folder(DOWNLOAD_DIR)  # wipe old files
        latest_file = get_latest_downloaded_file(DOWNLOAD_DIR)
        if latest_file:
            st.success(f"✅ Found downloaded file: {os.path.basename(latest_file)}")
            source_file = latest_file
        else:
            st.error("❌ No new Excel file found in raw folder.")
            source_file = None

# --- Preprocess & Upload ---
if st.button("⚙️ Preprocess & Upload to MongoDB"):
    if source_file:
        try:
            df = load_and_preprocess_alarm_file(source_file, PROCESSED_OUTPUT)
            st.success("✅ Preprocessing complete.")

            records = df_to_dicts(df)
            insert_bulk_alarms(records, COLLECTION_NAME)
            st.success("✅ Data inserted into MongoDB.")
        except Exception as e:
            st.error(f"❌ Error during processing: {e}")
    else:
        st.warning("⚠️ No file selected or detected.")

# --- Escalation ---
if st.button("📣 Escalate Alarms via Telegram"):
    try:
        escalate_alarms()   # ✅ no arguments now
        st.success("📢 Telegram alarm escalation completed.")
    except Exception as e:
        st.error(f"❌ Escalation failed: {e}")
