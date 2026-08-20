import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Target Year & Category
TARGET_YEAR = 2025
TARGET_CATEGORY = "Engineering"

# NIRF URLs
RANKING_URL_2025 = "https://www.nirfindia.org/Rankings/2025/EngineeringRanking.html"
RANK_BAND_URLS_2025 = {
    "101-150": "https://www.nirfindia.org/Rankings/2025/EngineeringRanking150.html",
    "151-200": "https://www.nirfindia.org/Rankings/2025/EngineeringRanking200.html",
    "201-300": "https://www.nirfindia.org/Rankings/2025/EngineeringRanking300.html",
}

# Request Configuration
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}
REQUEST_TIMEOUT = 30.0
MAX_CONCURRENT_DOWNLOADS = 5

# Google Sheets & Drive Configuration
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
GOOGLE_SHEET_TITLE = f"NIRF_{TARGET_YEAR}_{TARGET_CATEGORY}_Data"
GOOGLE_DRIVE_FOLDER_ID = "1Dz4gpSzJi2tYhrI8Zpn53S7GVGF1kfdN"
LOCAL_EXCEL_FILENAME = OUTPUTS_DIR / f"NIRF_{TARGET_YEAR}_{TARGET_CATEGORY}_Data.xlsx"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
