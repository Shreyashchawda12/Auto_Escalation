import logging
import requests
import pandas as pd
import re
from utils.config import BOT_TOKEN, TEST_MODE, TEST_CHAT_ID

# --- Config ---
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
MAX_LEN = 4000  # Telegram safe limit

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ---------------------------
# Escape Helpers
# ---------------------------
def escape_markdown(text: str) -> str:
    if pd.isna(text):
        return ""
    escape_chars = r'_*`\[\]()~>#+=|{}.!-'
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", str(text))


# ---------------------------
# Telegram Send Helpers
# ---------------------------
def send_telegram_message(chat_id: int, text: str, parse_mode="HTML") -> bool:
    """Send message to Telegram chat and log result. Redirect to TEST_CHAT_ID if TEST_MODE is enabled."""
    target_chat = int(TEST_CHAT_ID) if TEST_MODE and TEST_CHAT_ID else chat_id

    payload = {"chat_id": target_chat, "text": text, "parse_mode": parse_mode}
    response = requests.post(TELEGRAM_API_URL, data=payload)

    if response.status_code == 200:
        logging.info(f"✅ Sent message to {target_chat} ({'TEST' if TEST_MODE else 'LIVE'})")
        return True
    else:
        logging.error(f"❌ Failed to send to {target_chat}: {response.text}")
        return False


def safe_send(chat_id, message):
    """Send only if chat_id is valid numeric string."""
    if pd.notna(chat_id) and str(chat_id).isdigit():
        return send_telegram_message(int(chat_id), message)


def split_and_send(chat_id, full_message):
    """Split long messages into safe chunks for Telegram."""
    while len(full_message) > MAX_LEN:
        part = full_message[:MAX_LEN]
        safe_send(chat_id, part)
        full_message = full_message[MAX_LEN:]
    if full_message.strip():
        safe_send(chat_id, full_message)


# ---------------------------
# Message Builders
# ---------------------------
def build_site_message(site_id, site_df, role, site_down=False):
    """Build grouped escalation message including site, operator, and alarms."""

    # --- Site Info ---
    if "SiteName" in site_df:
        site_name = site_df["SiteName"].iloc[0]
    elif "SITE_NAME" in site_df:
        site_name = site_df["SITE_NAME"].iloc[0]
    else:
        site_name = "Unknown"

    if "Cluster" in site_df:
        cluster = site_df["Cluster"].iloc[0]
    elif "ONE_ATC_CLUSTER" in site_df:
        cluster = site_df["ONE_ATC_CLUSTER"].iloc[0]
    else:
        cluster = "Unknown"

    # --- Header ---
    if site_down:
        header = "🚨 <b>Site Down Alert</b>"
    else:
        header = f"🚨 <b>{role} Alarm Escalation</b>"

    msg = (
        f"{header}\n\n"
        f"<b>Site ID:</b> {site_id}\n"
        f"<b>Site Name:</b> {site_name}\n"
        f"<b>Cluster:</b> {cluster}\n\n"
    )

    # --- Alarm Details ---
    for _, row in site_df.iterrows():
        time_str = (
            row["OpenTime"].strftime("%Y-%m-%d %H:%M")
            if "OpenTime" in row and pd.notna(row["OpenTime"])
            else "Unknown"
        )
        tt_number = row.get("TTNumber", "N/A")
        operator = row.get("SourceInput", "Unknown")
        alarm_text = (
            row.get("Standard_Alarm_Name")
            if "Standard_Alarm_Name" in row
            else row.get("EventName", "")
        )

        msg += (
            f"• <b>Alarm:</b> {alarm_text}\n"
            f"  🕐 {time_str} | 🎫 TT: {tt_number}\n"
            f"  👤 Operator: {operator}\n\n"
        )

    return msg


def send_site_message(chat_id, site_id, site_df, role, site_down=False):
    """Build and send site message, auto-splitting if needed."""
    full_message = build_site_message(site_id, site_df, role, site_down)
    split_and_send(chat_id, full_message)
