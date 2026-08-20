import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper import scrape_all_rankings, scrape_top_100_rankings
from src.downloader import download_all_pdfs
from src.pdf_parser import extract_institute_data_from_pdf
from src.normalizer import normalize_all_data
from src.sheets_sync import export_to_excel, export_to_google_sheets
from config import (
    LOCAL_EXCEL_FILENAME,
    CREDENTIALS_FILE,
    DOWNLOADS_DIR,
    TARGET_YEAR,
    TARGET_CATEGORY,
)


def run_pipeline(
    limit: int = None,
    include_bands: bool = False,
    do_scrape: bool = True,
    do_download: bool = True,
    do_parse: bool = True,
    do_excel: bool = True,
    do_sheets: bool = True,
):
    print("=" * 60)
    print("  NIRF 2025 ENGINEERING DATA EXTRACTION & CURATION PIPELINE")
    print("=" * 60)

    # 1. SCRAPE RANKINGS
    if do_scrape:
        print("\n[Step 1/5] Scraping NIRF Rankings HTML...")
        if include_bands:
            rankings = scrape_all_rankings(include_bands=True)
        else:
            rankings = scrape_top_100_rankings()
            
        if limit:
            print(f"[Pipeline] Limiting to first {limit} institutes.")
            rankings = rankings[:limit]
    else:
        print("\n[Step 1/5] Skipping Scraping (assuming already cached).")
        return

    # 2. DOWNLOAD PDFS
    if do_download:
        print(f"\n[Step 2/5] Downloading {len(rankings)} institute submitted PDFs...")
        rankings = download_all_pdfs(rankings)
    else:
        print("\n[Step 2/5] Skipping PDF Downloads.")

    # 3. PARSE PDF TABLES
    parsed_pdf_results = []
    if do_parse:
        print("\n[Step 3/5] Extracting tables from submitted institute PDFs...")
        pdf_folder = DOWNLOADS_DIR / str(TARGET_YEAR) / TARGET_CATEGORY
        for r in tqdm(rankings, desc="Parsing PDF Tables"):
            inst_id = r.get("institute_id", "")
            name = r.get("institute_name", "")
            clean_id = inst_id.replace("/", "_").replace("\\", "_")
            
            # Check local_pdf_path or fallback to default download folder
            pdf_path = r.get("local_pdf_path")
            if not pdf_path or not Path(pdf_path).exists():
                candidate = pdf_folder / f"{clean_id}.pdf"
                if candidate.exists():
                    pdf_path = str(candidate)

            if pdf_path and Path(pdf_path).exists():
                extracted = extract_institute_data_from_pdf(pdf_path, inst_id, name)
                parsed_pdf_results.append(extracted)
            else:
                parsed_pdf_results.append({
                    "institute_id": inst_id,
                    "institute_name": name,
                })
    else:
        print("\n[Step 3/5] Skipping PDF Parsing.")

    # 4. NORMALIZE & STRUCTURE DATA
    print("\n[Step 4/5] Normalizing and validating relational schemas...")
    tables_dict = normalize_all_data(rankings, parsed_pdf_results)

    print("\nSummary of Extracted Relational Tables:")
    for tab_name, df in tables_dict.items():
        print(f"  • {tab_name:<28}: {len(df):>5} records (columns: {len(df.columns)})")

    # 5. EXPORT
    print("\n[Step 5/5] Exporting Data...")
    if do_excel:
        excel_path = export_to_excel(tables_dict, output_file=LOCAL_EXCEL_FILENAME)

    if do_sheets:
        export_to_google_sheets(tables_dict)

    print("\n" + "=" * 60)
    print("  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="NIRF 2025 Engineering Data Scraping and Table Extraction Pipeline"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="Run entire pipeline (Scrape -> Download -> Parse -> Excel & Sheets)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of colleges to process (e.g. --limit 5 for a quick test)",
    )
    parser.add_argument(
        "--include-bands",
        action="store_true",
        default=False,
        help="Include 101-300 rank band institutions in Master Rankings",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip downloading PDFs (use already cached PDFs)",
    )
    parser.add_argument(
        "--skip-sheets",
        action="store_true",
        help="Skip Google Sheets API upload (export to Excel only)",
    )

    args = parser.parse_args()

    run_pipeline(
        limit=args.limit,
        include_bands=args.include_bands,
        do_scrape=True,
        do_download=not args.skip_download,
        do_parse=True,
        do_excel=True,
        do_sheets=not args.skip_sheets,
    )


if __name__ == "__main__":
    main()
