🚨 Alarm Automation & Escalation System

This project automates the processing and escalation of telecom network alarms.
It handles downloading or manually uploading alarm logs, preprocessing them, storing them in MongoDB, and sending real-time escalations to field teams via Telegram Bot.

📌 Features

Manual Alarm Log Input

Upload alarm files (.xlsx / .csv) manually in the dashboard.

Or place VNOC-downloaded logs in the data/raw/ folder.

Preprocessing

Cleans and normalizes alarm logs.

Stores processed alarms in data/processed/cleaned_alarms.csv.

MongoDB Integration

Uploads alarm data into MongoDB for long-term storage and analysis.

Telegram Escalation

Sends alarm notifications to Technicians, Supervisors, and Cluster Engineers.

CE escalation is triggered only for 2G/3G/4G outage alarms.

Supports test mode (all messages go to your test chat ID).

Streamlit Dashboard

Simple UI for selecting input mode, preprocessing, uploading, and triggering escalation.

📂 Project Structure
autocall/
│── app.py                         # Streamlit dashboard
│── automation/
│   └── download_and_preprocess.py # Helpers for manual download
│── data/
│   ├── raw/                       # VNOC raw files (manual download here)
│   ├── processed/                 # Cleaned alarms
│   └── mapping/                   # Site escalation mapping file
│── mongodb/
│   └── mongo_crud.py              # MongoDB helpers
│── telegram_bot/
│   ├── escalate_alarms.py         # Main escalation logic
│   └── telegram_utils.py          # Telegram helpers
│── utils/
│   ├── config.py                  # Global config (paths, tokens, test mode)
│   ├── mongo_utils.py             # DataFrame → Mongo helpers
│   └── preprocessor.py            # File cleaning logic
│── .env                           # Secrets (Mongo, Telegram, VNOC login)
│── requirements.txt
│── README.md

⚙️ Setup
1. Clone & Install
git clone <repo-url>
cd autocall
pip install -r requirements.txt

2. Configure Environment

Create a .env file in the root:

# MongoDB
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net
MONGO_DB=TELCOM_AI

# Telegram Bot
BOT_TOKEN=123456789:ABC-YourBotToken
TEST_MODE=True
TEST_CHAT_ID=6048553594

# VNOC login (only if auto-download is used later)
VNOC_USERNAME=your_username
VNOC_PASSWORD=your_password

3. Prepare Data

Place site escalation mapping file in:
data/mapping/site_escalation_mapping.xlsx
(contains Technician, Supervisor, CE contact + chat IDs)

For manual upload, select a file from Streamlit.

For manual download, place your VNOC-exported file in data/raw/.

▶️ Run the Dashboard
streamlit run app.py

🚀 Usage Flow

Select Input Mode

📤 Manual Upload → Upload alarm file.

🖐 Manual Download → Place VNOC file in data/raw/.

Preprocess & Upload

Cleans alarm logs.

Saves cleaned_alarms.csv.

Inserts into MongoDB.

Escalate Alarms

Technician & Supervisor → get all alarms for their sites.

CE → only receives 2G/3G/4G outage alarms.

In TEST_MODE, all alarms go to your test chat ID.

📡 Example Escalation Message
🚨 Technician Alarm Escalation

Site ID: 594763
Site Name: Vidyanagar
Cluster: PUNE-3

• Alarm: SITE ON BATTERY
  🕐 2025-03-10 00:20 | 🎫 TT: TT699580536
  👤 Operator: Airtel

• Alarm: MAINS FAIL/EB FAIL
  🕐 2025-03-10 00:21 | 🎫 TT: TT699580537
  👤 Operator: Airtel

🛠 Tech Stack

Python (pandas, requests, selenium, pymongo, streamlit)

MongoDB Atlas (cloud database for storing alarms)

Telegram Bot API (real-time escalation)

Streamlit (dashboard UI)

🔮 Next Steps

Add auto-download from VNOC (currently manual).

Add role-based dashboards (Technician/Supervisor/CE).

Support alert filtering (latest-only, outage-only, etc.).

Integration with ML models for site-down prediction.

👉 This is a production-ready skeleton, and you can extend it to predictive analytics or RAG insights later.