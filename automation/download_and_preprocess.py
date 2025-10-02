import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import preprocessing
from utils.preprocessor import load_and_preprocess_alarm_file

# --- Config ---
DOWNLOAD_DIR = os.path.abspath("data/raw")
PROCESSED_OUTPUT = "data/processed/cleaned_alarms.csv"
USERNAME = os.getenv("VNOC_USERNAME")
PASSWORD = os.getenv("VNOC_PASSWORD")

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


if not USERNAME or not PASSWORD:
    logging.error("❌ VNOC credentials missing in .env file")
    sys.exit(1)



# ---------------------------
# Helpers
# ---------------------------
def setup_driver(download_dir):
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def wait_for_element(driver, locator, timeout=20, condition=EC.presence_of_element_located):
    return WebDriverWait(driver, timeout).until(condition(locator))


def clear_download_folder(folder):
    """Delete all old files in raw download folder before starting."""
    if os.path.exists(folder):
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            try:
                os.remove(path)
            except Exception as e:
                logging.warning(f"Could not remove {path}: {e}")
        logging.info(f"🧹 Cleared old files in {folder}")
    else:
        os.makedirs(folder, exist_ok=True)
        logging.info(f"📂 Created folder: {folder}")


def wait_for_new_file(folder, timeout=120):
    """
    Wait until a new Excel file appears in the folder.
    Returns the file path if found, else None.
    """
    logging.info("⏳ Waiting for a new Excel file in raw folder...")
    end_time = time.time() + timeout
    seen = set(os.listdir(folder))  # track current files

    while time.time() < end_time:
        current_files = set(os.listdir(folder))
        new_files = [f for f in current_files - seen if f.endswith(".xlsx")]
        if new_files:
            new_path = os.path.join(folder, new_files[0])
            logging.info(f"✅ Detected new Excel file: {new_path}")
            return new_path
        time.sleep(3)

    logging.error("❌ No new Excel file detected within timeout.")
    return None


# ---------------------------
# Main Workflow
# ---------------------------
def download_alarm_log():
    """Login and navigate to TT Log page. You can manually click 'Download Excel'."""
    driver = setup_driver(DOWNLOAD_DIR)
    try:
        logging.info("🔑 Opening login page...")
        driver.get("https://vnoc.atctower.in/vnoc/Default.aspx")

        wait_for_element(driver, (By.NAME, 'appLogin$UserName')).send_keys(USERNAME)
        driver.find_element(By.NAME, 'appLogin$Password').send_keys(PASSWORD)
        driver.find_element(By.NAME, 'appLogin$LoginImageButton').click()

        wait_for_element(driver, (By.ID, 'ctl00_Html1'))  # Post-login page

        logging.info("📥 Navigating to TT Log page...")
        driver.get("https://vnoc.atctower.in/vnoc/aspx/TroubleTicketLogDetail.aspx")
        wait_for_element(driver, (By.ID, 'aspnetForm'))

        # Wait for loading overlay
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(),'Loading....')]"))
        )

        logging.info("✅ TT Log page ready. Please manually click 'Download Excel' if auto export fails.")

        return driver  # keep browser open so you can click manually

    except Exception as e:
        logging.error(f"Login or navigation failed: {e}")
        driver.quit()
        return None


def get_latest_downloaded_file(folder):
    """Return most recent .xlsx file in folder."""
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".xlsx")]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


# ---------------------------
# Runner
# ---------------------------
if __name__ == "__main__":
    logging.info("🚀 Starting alarm log collection pipeline...")

    # Step 1: clear raw folder
    clear_download_folder(DOWNLOAD_DIR)

    # Step 2: open VNOC (manual/auto download)
    driver = download_alarm_log()
    if not driver:
        logging.error("❌ Could not open VNOC portal.")
        sys.exit(1)

    # Step 3: wait for file
    latest_file = wait_for_new_file(DOWNLOAD_DIR, timeout=180)

    # Step 4: process if found
    if latest_file:
        logging.info(f"📂 Latest file: {latest_file}")
        df = load_and_preprocess_alarm_file(latest_file, PROCESSED_OUTPUT)
        logging.info("✅ Preprocessing complete.")
    else:
        logging.warning("❌ No Excel file downloaded.")

    # Step 5: keep browser open for debugging, or close if you want
    try:
        input("🔍 Press Enter to close browser...")
    finally:
        driver.quit()
