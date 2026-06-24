import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set (used to encrypt stored TikTok cookies)")

PANEL_USERNAME = os.environ.get("PANEL_USERNAME", "admin")
PANEL_PASSWORD = os.environ.get("PANEL_PASSWORD", "")
if not PANEL_PASSWORD:
    raise RuntimeError("PANEL_PASSWORD must be set to protect the web panel")

STORAGE_RAW = os.environ.get("STORAGE_RAW", "/data/storage/raw")
STORAGE_PROCESSED = os.environ.get("STORAGE_PROCESSED", "/data/storage/processed")
STORAGE_WATERMARKS = os.environ.get("STORAGE_WATERMARKS", "/data/storage/watermarks")
