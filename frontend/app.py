import os
import sys
import logging
import streamlit as st
import pandas as pd

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.preprocessor import load_and_preprocess_alarm_file
from telegram_bot.escalate_alarms import escalate_alarms
from mongodb.mongo_crud import insert_bulk_alarms
from automation.download_and_preprocess import (
    get_latest_downloaded_file,
    clear_download_folder,
    download_alarm_log,      # ✅ works locally only
    wait_for_new_file        # ✅ works locally only
)
from utils.mongo_utils import df_to_dicts

# Constants
DOWNLOAD_DIR = os.path.abspath("data/raw")
PROCESSED_OUTPUT = "data/processed/cleaned_alarms.csv"
COLLECTION_NAME = "AlarmLogs"

# --- Initialize session state ---
if "source_file" not in st.session_state:
    st.session_state["source_file"] = None

# UI
st.title("🚨 Alarm Automation Dashboard")

mode = st.radio("Choose Input Mode", ["📤 Manual Upload" ,"🖐 Auto Download (VNOC)"])

# --- Manual Upload ---
if mode == "📤 Manual Upload":
    uploaded_file = st.file_uploader("Upload Alarm Log File", type=["xlsx", "csv"])
    if uploaded_file is not None:
        uploaded_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)
        with open(uploaded_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["source_file"] = uploaded_path
        st.success(f"📂 Uploaded file saved: {uploaded_file.name}")

# --- Manual Download ---
else:
    st.info("👉 Download the alarm log file from VNOC.")
    if st.button("🔄 Get File from VNOC"):
        try:
            # Detect environment
            if os.getenv("STREAMLIT_RUNTIME"):  
                # 🚀 Cloud mode → no Selenium, just check for file in raw folder
                latest_file = get_latest_downloaded_file(DOWNLOAD_DIR)
                if latest_file:
                    st.session_state["source_file"] = latest_file
                    st.success(f"✅ Found downloaded file: {os.path.basename(latest_file)}")
                else:
                    st.error("❌ No Excel file found in raw folder. Please upload manually.")
            else:
                # 🖥 Local mode → use Selenium
                clear_download_folder(DOWNLOAD_DIR)
                driver = download_alarm_log()
                if not driver:
                    st.error("❌ Failed to open VNOC portal.")
                else:
                    latest_file = wait_for_new_file(DOWNLOAD_DIR, timeout=180)
                    driver.quit()
                    if latest_file:
                        st.session_state["source_file"] = latest_file
                        st.success(f"✅ Detected new Excel file: {os.path.basename(latest_file)}")
                    else:
                        st.error("❌ No new Excel file detected in raw folder.")
        except Exception as e:
            st.error(f"❌ Error during manual download: {e}")

# --- Preprocess & Upload ---
if st.button("⚙️ Preprocess & Upload to MongoDB"):
    source_file = st.session_state.get("source_file")
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
        escalate_alarms()
        st.success("📢 Telegram alarm escalation completed.")
    except Exception as e:
        st.error(f"❌ Escalation failed: {e}")
