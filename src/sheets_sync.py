import sys
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CREDENTIALS_FILE, GOOGLE_SHEET_TITLE, GOOGLE_DRIVE_FOLDER_ID, LOCAL_EXCEL_FILENAME


def export_to_excel(tables_dict: Dict[str, pd.DataFrame], output_file: Path = LOCAL_EXCEL_FILENAME) -> str:
    """
    Exports all normalized tables into a single multi-tab Excel workbook with formatted headers.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"[Excel Exporter] Writing multi-tab Excel workbook to: {output_file}")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for tab_name, df in tables_dict.items():
            # Truncate tab name if over 31 chars (Excel limit)
            safe_tab = tab_name[:31]
            df.to_excel(writer, sheet_name=safe_tab, index=False)

    print(f"[Excel Exporter] Successfully saved {len(tables_dict)} sheets to {output_file}")
    return str(output_file)


def export_to_google_sheets(
    tables_dict: Dict[str, pd.DataFrame],
    sheet_title: str = GOOGLE_SHEET_TITLE,
    credentials_path: Path = CREDENTIALS_FILE,
) -> Optional[str]:
    """
    Syncs normalized tables to Google Sheets using Google Service Account credentials.
    """
    if not credentials_path.exists():
        print("\n" + "=" * 70)
        print("[Google Sheets Sync] Note: credentials.json not found.")
        print("To sync directly with Google Sheets:")
        print("1. Go to Google Cloud Console -> Create Service Account")
        print("2. Enable Google Sheets API & Google Drive API")
        print("3. Generate & download JSON key -> save as 'credentials.json' in this folder.")
        print(f"4. Offline Excel backup was saved to: {LOCAL_EXCEL_FILENAME}")
        print("=" * 70 + "\n")
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    try:
        print(f"[Google Sheets Sync] Authenticating with {credentials_path}...")
        gc = gspread.service_account(filename=str(credentials_path), scopes=scopes)

        print(f"[Google Sheets Sync] Opening or creating spreadsheet '{sheet_title}'...")
        try:
            sh = gc.open(sheet_title)
        except gspread.SpreadsheetNotFound:
            if GOOGLE_DRIVE_FOLDER_ID:
                print(f"[Google Sheets Sync] Creating spreadsheet inside Google Drive folder '{GOOGLE_DRIVE_FOLDER_ID}'...")
                sh = gc.create(sheet_title, folder_id=GOOGLE_DRIVE_FOLDER_ID)
            else:
                sh = gc.create(sheet_title)

        for tab_name, df in tables_dict.items():
            safe_tab = tab_name[:31]
            print(f"  -> Updating tab: '{safe_tab}' ({len(df)} rows)...")
            
            # Open or create tab
            try:
                ws = sh.worksheet(safe_tab)
                ws.clear()
            except gspread.WorksheetNotFound:
                ws = sh.add_worksheet(
                    title=safe_tab,
                    rows=max(100, len(df) + 10),
                    cols=max(10, len(df.columns) + 5),
                )

            # Fill missing values and build 2D array
            clean_df = df.fillna("")
            payload = [clean_df.columns.values.tolist()] + clean_df.values.tolist()

            if payload:
                ws.update(payload, value_input_option="USER_ENTERED")
                # Format Header: Bold and Freeze Row 1
                try:
                    ws.freeze(rows=1)
                    ws.format("1:1", {"textFormat": {"bold": True}})
                except Exception:
                    pass

        # Remove default 'Sheet1' if it's empty and unused
        try:
            default_ws = sh.worksheet("Sheet1")
            if default_ws and "Sheet1" not in tables_dict:
                sh.del_worksheet(default_ws)
        except Exception:
            pass

        print(f"\n[Google Sheets Sync] ✅ Sync Complete!")
        print(f"[Google Sheets Sync] Spreadsheet URL: {sh.url}\n")
        return sh.url

    except Exception as e:
        print(f"[Google Sheets Sync] Error uploading to Google Sheets: {e}")
        return None
