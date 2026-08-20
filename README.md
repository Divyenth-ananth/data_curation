# NIRF 2025 Engineering Data Curation & Extraction Pipeline

An automated data pipeline to scrape the **National Institutional Ranking Framework (NIRF) 2025 Engineering Rankings**, download submitted institution PDF reports, extract all multi-page tables, normalize the schemas, and export structured data into **Google Sheets** and **multi-tab Excel workbooks**.

---

## 📁 Project Structure

```text
data_curation/
├── config.py                 # Target year, URLs, output paths & Google Sheets title
├── run.py                    # Main pipeline CLI orchestrator
├── credentials.json          # (Optional) Google Cloud Service Account credentials
├── src/
│   ├── scraper.py            # Web scraper for NIRF ranking pages & PDF URLs
│   ├── downloader.py         # Async batch PDF downloader with disk caching
│   ├── pdf_parser.py         # PDF table extractor powered by pdfplumber
│   ├── normalizer.py         # Currency parser, schema validation & DataFrame builder
│   ├── schemas.py            # Pydantic data models
│   └── sheets_sync.py        # Multi-tab Google Sheets (gspread) & Excel exporter
├── downloads/                # Local cache for downloaded institute PDFs
└── outputs/                  # Exported Excel workbooks (.xlsx)
```

---

## 📊 Extracted Relational Tables

The pipeline extracts and structures 7 relational tabs:

| Tab Name | Description | Key Fields |
| :--- | :--- | :--- |
| **`Rankings_Master`** | Official NIRF 2025 Engineering ranks | Institute ID, Name, City, State, Score, Rank, TLR, RPC, GO, OI, Perception, PDF URL |
| **`Sanctioned_Intake`** | Approved student intake per program | Program (UG 4-Yr, PG 2-Yr, etc.), Intakes for 2023-24 down to 2018-19 |
| **`Student_Demographics`** | Student strength & demographic breakdown | Male, Female, Total, In-State, Out-State, International, Economically Backward, Socially Challenged, Reimbursement metrics |
| **`Placements_and_Salaries`**| Placement stats & median CTC | Academic Year, Intake, Admitted, Lateral, Graduating, Placed, Median Salary (INR Numeric), Higher Studies count |
| **`Financial_Expenditures`** | Capital & Operational expenditures | Category, Item Description, 2023-24 INR, 2022-23 INR, 2021-22 INR |
| **`Research_and_Consultancy`**| Sponsored research & consultancy projects | Metric, Project counts, Client count, Funding amount in INR |
| **`Faculty_Roster`** | Faculty members list | Name, Age, Designation, Gender, Qualification, Experience (Months), Joining date |

---

## 🚀 How to Run

### Step 1: Activate your Conda environment
```bash
conda activate data_curation
```

### Step 2: Quick Test (Top 5 Colleges)
Run a test extraction on the top 5 colleges (IIT Madras, IIT Delhi, IIT Bombay, IIT Kanpur, IIT Kharagpur):
```bash
python run.py --limit 5
```
*This downloads the 5 PDFs, extracts all tables, and generates a formatted Excel file at `outputs/NIRF_2025_Engineering_Data.xlsx`.*

---

### Step 3: Full Run (Top 100 Colleges)
To extract all Top 100 Engineering colleges:
```bash
python run.py
```

### Step 4: Include 101–300 Rank Band Colleges in Master Sheet
```bash
python run.py --include-bands
```

---

## 📑 Google Sheets Setup (Optional)

If you want the pipeline to sync directly to your Google Drive / Google Sheets:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `NIRF-Data-Curation`).
3. Enable **Google Sheets API** and **Google Drive API**.
4. Go to **Credentials** $\to$ **Create Credentials** $\to$ **Service Account**.
5. Create a key in **JSON format** and save it as `credentials.json` in this `data_curation/` directory.
6. Share your target Google Sheet with the Service Account email (found inside `credentials.json`), or let the script auto-create the sheet in the Service Account's Drive.

*Note: If `credentials.json` is not present, the pipeline automatically saves everything to `outputs/NIRF_2025_Engineering_Data.xlsx` without failing.*
