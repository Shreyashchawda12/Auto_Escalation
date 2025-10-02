import os, requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TEST_CHAT_ID")   # use your own chat id

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": "🚨 Test direct send!"}

resp = requests.post(url, data=payload)
print(resp.status_code, resp.text)
