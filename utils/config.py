import os
from dotenv import load_dotenv
import pandas as pd

# Load .env once at startup
load_dotenv()

# --- Telegram ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_CHAT_ID = os.getenv("TEST_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN missing in .env file")

# --- Files ---
CLEANED_ALARM_FILE = "data/processed/cleaned_alarms.csv"
MAPPING_FILE = "data/reference/Alarm_Escalation_Matrix.xlsx"

# --- Escalation threshold (Cluster Engineer) ---
# Default: 1 hour
LONG_PENDING_THRESHOLD = pd.Timedelta(hours=1)
