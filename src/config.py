import os
import json

# GitHub Secretsから読み込む設定値
GCP_SA_KEY = json.loads(os.environ.get("GCP_SA_KEY", "{}"))
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")

# 固定設定
SHEET_NAME = "保有銘柄2512"
