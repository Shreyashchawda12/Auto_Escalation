import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_and_preprocess_alarm_file(file_path: str, output_path: str) -> pd.DataFrame:
    """
    Load, clean, and preprocess the raw TTLog alarm file.
    - Keeps only required columns
    - Normalizes headers
    - Parses timestamps
    - Removes cleared alarms
    - Detects site-down alarms (2G/3G/4G outage)
    - Saves cleaned CSV for escalation
    """

    # Load Excel, row 1 is actual header
    df = pd.read_excel(file_path, header=1)

    # Required columns
    required_columns = [
        "OpenTime", "TTNumber", "Cluster", "SiteID", "SiteName",
        "SourceInput", "EventName", "ClusterEngineer", "Technician",
        "EsclationStatus", "ClearedDateTime"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise KeyError(f"⚠️ Missing required columns in alarm file: {missing}")

    # Subset + normalize
    df = df[required_columns].copy()
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    # Parse timestamps
    df["OpenTime"] = pd.to_datetime(df["OpenTime"], errors="coerce")
    df["ClearedDateTime"] = pd.to_datetime(df["ClearedDateTime"], errors="coerce")

    # Keep only active alarms
    before_count = len(df)
    df = df[df["ClearedDateTime"].isna()].copy()
    after_count = len(df)
    print(f"⚡ Removed {before_count - after_count} cleared alarms. Remaining active: {after_count}")

    # Detect site-down based on EventName
    outage_keywords = ["2G OUTAGE", "3G OUTAGE", "4G OUTAGE"]
    df["Is_SiteDown"] = df["EventName"].str.upper().isin(outage_keywords)

    # Drop ClearedDateTime (not needed anymore)
    df.drop(columns=["ClearedDateTime"], inplace=True)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ Cleaned & filtered file saved at: {output_path}")
    return df
