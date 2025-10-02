import pandas as pd
from utils.config import CLEANED_ALARM_FILE, MAPPING_FILE
from telegram_bot.telegram_utils import send_site_message


def valid_chat_id(x):
    """Convert chat_id from float/string to int, return None if invalid."""
    try:
        return int(float(x))
    except:
        return None


def load_and_merge():
    """Load alarms + mapping files, normalize columns, merge and return final DataFrame."""
    alarm_df = pd.read_csv(CLEANED_ALARM_FILE)
    mapping_df = pd.read_excel(MAPPING_FILE)

    # Normalize columns
    alarm_df.columns = alarm_df.columns.str.strip().str.replace(" ", "_")
    mapping_df.columns = mapping_df.columns.str.strip().str.replace(" ", "_")

    # Ensure IDs are strings
    alarm_df["SiteID"] = alarm_df["SiteID"].astype(str)
    mapping_df["GLOBAL_ID"] = mapping_df["GLOBAL_ID"].astype(str)

    # Merge
    merged_df = pd.merge(alarm_df, mapping_df, left_on="SiteID", right_on="GLOBAL_ID", how="left")

    # Normalize OpenTime & EventName
    merged_df["OpenTime"] = pd.to_datetime(merged_df["OpenTime"], errors="coerce")
    merged_df["EventName"] = merged_df["EventName"].astype(str).str.strip().str.upper()

    return merged_df


def escalate_alarms():
    df = load_and_merge()

    print("✅ Columns after merge:", df.columns.tolist())
    print("🔍 Total alarms loaded:", len(df))

    tech_count, sup_count, ce_count = 0, 0, 0

    # --- Group per SiteID ---
    for site_id, site_df in df.groupby("SiteID"):

        # Technician escalation → ALL alarms for this site
        tech_ids = site_df["Technician_Chat_id"].dropna().unique() if "Technician_Chat_id" in site_df else []
        for tid in tech_ids:
            cid = valid_chat_id(tid)
            if cid:
                send_site_message(cid, site_id, site_df, "Technician")
                tech_count += len(site_df)

        # Supervisor escalation → ALL alarms for this site
        sup_ids = site_df["Supervisor_Chat_id"].dropna().unique() if "Supervisor_Chat_id" in site_df else []
        for sid in sup_ids:
            cid = valid_chat_id(sid)
            if cid:
                send_site_message(cid, site_id, site_df, "Supervisor")
                sup_count += len(site_df)

        # CE escalation → ONLY outages (2G/3G/4G)
        ce_df = site_df[site_df["EventName"].str.contains("2G OUTAGE|3G OUTAGE|4G OUTAGE", na=False)]
        ce_ids = ce_df["CE_Chat_id"].dropna().unique() if "CE_Chat_id" in ce_df else []
        for ceid in ce_ids:
            cid = valid_chat_id(ceid)
            if cid:
                send_site_message(cid, site_id, ce_df, "Cluster Engineer", site_down=True)
                ce_count += len(ce_df)

    # ✅ Final status
    print(f"📢 Escalation completed → 👷 Technician: {tech_count}, 🧑‍💼 Supervisor: {sup_count}, 👷‍♂️ CE: {ce_count}")


if __name__ == "__main__":
    escalate_alarms()
