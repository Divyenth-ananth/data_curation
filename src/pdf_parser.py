import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pdfplumber

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def clean_cell_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    # Replace line breaks and extra spaces
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    return cleaned


def extract_institute_data_from_pdf(pdf_path: str, institute_id: str, institute_name: str) -> Dict[str, Any]:
    """
    Parses an individual NIRF submitted institute PDF and extracts all standardized tables.
    """
    results = {
        "institute_id": institute_id,
        "institute_name": institute_name,
        "intake": [],
        "demographics": [],
        "placements": [],
        "phd": {},
        "capital_expenditure": [],
        "operational_expenditure": [],
        "sponsored_research": [],
        "consultancy": [],
        "faculty": []
    }

    if not pdf_path or not Path(pdf_path).exists():
        return results

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            all_tables = []
            
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        all_tables.append({
                            "page": page_idx + 1,
                            "page_text": page_text,
                            "raw_table": table
                        })

            # Process identified tables
            for tbl_info in all_tables:
                raw_table = tbl_info["raw_table"]
                if not raw_table or len(raw_table) < 2:
                    continue

                # Header text inspection
                header_row_0 = [clean_cell_text(c) for c in raw_table[0]]
                header_combined = " ".join(header_row_0).lower()
                first_col_text = clean_cell_text(raw_table[0][0]).lower()

                # 1. Sanctioned Intake
                # Header: ['Academic Year', '2023-24', '2022-23', '2021-22', '2020-21', ...]
                if "academic year" in first_col_text and len(header_row_0) >= 6 and any("ug" in clean_cell_text(r[0]).lower() or "pg" in clean_cell_text(r[0]).lower() for r in raw_table[1:]):
                    for row in raw_table[1:]:
                        prog = clean_cell_text(row[0])
                        if not prog or prog.lower() == "academic year":
                            continue
                        results["intake"].append({
                            "program": prog,
                            "intake_2023_24": clean_cell_text(row[1]) if len(row) > 1 else "",
                            "intake_2022_23": clean_cell_text(row[2]) if len(row) > 2 else "",
                            "intake_2021_22": clean_cell_text(row[3]) if len(row) > 3 else "",
                            "intake_2020_21": clean_cell_text(row[4]) if len(row) > 4 else "",
                            "intake_2019_20": clean_cell_text(row[5]) if len(row) > 5 else "",
                            "intake_2018_19": clean_cell_text(row[6]) if len(row) > 6 else "",
                        })

                # 2. Student Demographics & Strength
                # Headers have 'No. of Male Students', 'No. of Female Students', 'Total Students', etc.
                elif any("male" in h for h in header_row_0) and any("female" in h for h in header_row_0) and any("total" in h for h in header_row_0):
                    for row in raw_table[1:]:
                        prog = clean_cell_text(row[0])
                        if not prog or "program" in prog.lower() and "all" in prog.lower():
                            continue
                        results["demographics"].append({
                            "program": prog,
                            "male_students": clean_cell_text(row[1]) if len(row) > 1 else "",
                            "female_students": clean_cell_text(row[2]) if len(row) > 2 else "",
                            "total_students": clean_cell_text(row[3]) if len(row) > 3 else "",
                            "within_state": clean_cell_text(row[4]) if len(row) > 4 else "",
                            "outside_state": clean_cell_text(row[5]) if len(row) > 5 else "",
                            "outside_country": clean_cell_text(row[6]) if len(row) > 6 else "",
                            "economically_backward": clean_cell_text(row[7]) if len(row) > 7 else "",
                            "socially_challenged": clean_cell_text(row[8]) if len(row) > 8 else "",
                            "reimbursement_govt": clean_cell_text(row[9]) if len(row) > 9 else "",
                            "reimbursement_institution": clean_cell_text(row[10]) if len(row) > 10 else "",
                            "reimbursement_private": clean_cell_text(row[11]) if len(row) > 11 else "",
                            "no_reimbursement": clean_cell_text(row[12]) if len(row) > 12 else "",
                        })

                # 3. Placement & Higher Studies
                # Headers contain 'Median salary', 'placed', 'graduating'
                elif any("median salary" in clean_cell_text(c).lower() for c in header_row_0) or any("placed" in clean_cell_text(c).lower() for c in header_row_0):
                    # Identify program name from surrounding text or table structure
                    program_label = "General"
                    p_text = tbl_info["page_text"]
                    for line in p_text.splitlines():
                        if any(k in line for k in ["UG [4 Years", "UG [5 Years", "PG [2 Year", "PG [3 Year", "PG-Integrated", "UG [3 Years"]):
                            program_label = line.strip()
                            break

                    for row in raw_table[1:]:
                        r_clean = [clean_cell_text(c) for c in row]
                        if not r_clean or len(r_clean) < 6:
                            continue
                        
                        # Placement tables have either 8 or 10 columns (with or without Lateral entry)
                        if len(r_clean) >= 10:
                            results["placements"].append({
                                "program": program_label,
                                "academic_year": r_clean[0],
                                "first_year_intake": r_clean[1],
                                "first_year_admitted": r_clean[2],
                                "lateral_year": r_clean[3],
                                "lateral_admitted": r_clean[4],
                                "graduating_year": r_clean[5],
                                "graduating_stipulated_time": r_clean[6],
                                "placed_students": r_clean[7],
                                "median_salary_raw": r_clean[8],
                                "selected_higher_studies": r_clean[9] if len(r_clean) > 9 else "",
                            })
                        elif len(r_clean) >= 7:
                            results["placements"].append({
                                "program": program_label,
                                "academic_year": r_clean[0],
                                "first_year_intake": r_clean[1],
                                "first_year_admitted": r_clean[2],
                                "lateral_year": "",
                                "lateral_admitted": "0",
                                "graduating_year": r_clean[3],
                                "graduating_stipulated_time": r_clean[4],
                                "placed_students": r_clean[5],
                                "median_salary_raw": r_clean[6],
                                "selected_higher_studies": r_clean[7] if len(r_clean) > 7 else "",
                            })

                # 4. Ph.D Student Details
                elif "ph.d" in header_combined or any("doctoral program" in clean_cell_text(r[0]).lower() for r in raw_table):
                    for row in raw_table:
                        row_txt = " ".join([clean_cell_text(c) for c in row if c])
                        if "full time" in row_txt.lower():
                            vals = [clean_cell_text(c) for c in row if c and clean_cell_text(c).isdigit()]
                            if vals and "full_time_pursuing" not in results["phd"]:
                                results["phd"]["full_time_pursuing"] = vals[0]
                        elif "part time" in row_txt.lower():
                            vals = [clean_cell_text(c) for c in row if c and clean_cell_text(c).isdigit()]
                            if vals and "part_time_pursuing" not in results["phd"]:
                                results["phd"]["part_time_pursuing"] = vals[0]

                # 5. Financial Resources (Capital & Operational Expenditure)
                elif "financial year" in first_col_text or any("utilised amount" in clean_cell_text(c).lower() for c in header_row_0):
                    is_operational = any("operational expenditure" in clean_cell_text(r[0]).lower() for r in raw_table)
                    is_capital = any("capital expenditure" in clean_cell_text(r[0]).lower() for r in raw_table)
                    
                    target_list = results["operational_expenditure"] if is_operational else results["capital_expenditure"]
                    
                    for row in raw_table[1:]:
                        item_desc = clean_cell_text(row[0])
                        if not item_desc or "expenditure" in item_desc.lower() or "utilised" in item_desc.lower():
                            continue
                        target_list.append({
                            "item_description": item_desc,
                            "year_2023_24_raw": clean_cell_text(row[1]) if len(row) > 1 else "",
                            "year_2022_23_raw": clean_cell_text(row[2]) if len(row) > 2 else "",
                            "year_2021_22_raw": clean_cell_text(row[3]) if len(row) > 3 else "",
                        })

                # 6. Sponsored Research Projects
                elif any("sponsored projects" in clean_cell_text(r[0]).lower() for r in raw_table):
                    for row in raw_table[1:]:
                        metric = clean_cell_text(row[0])
                        results["sponsored_research"].append({
                            "metric": metric,
                            "year_2023_24": clean_cell_text(row[1]) if len(row) > 1 else "",
                            "year_2022_23": clean_cell_text(row[2]) if len(row) > 2 else "",
                            "year_2021_22": clean_cell_text(row[3]) if len(row) > 3 else "",
                        })

                # 7. Consultancy Projects
                elif any("consultancy projects" in clean_cell_text(r[0]).lower() for r in raw_table):
                    for row in raw_table[1:]:
                        metric = clean_cell_text(row[0])
                        results["consultancy"].append({
                            "metric": metric,
                            "year_2023_24": clean_cell_text(row[1]) if len(row) > 1 else "",
                            "year_2022_23": clean_cell_text(row[2]) if len(row) > 2 else "",
                            "year_2021_22": clean_cell_text(row[3]) if len(row) > 3 else "",
                        })

                # 8. Faculty Details
                elif any("designation" in clean_cell_text(c).lower() for c in header_row_0) and any("qualification" in clean_cell_text(c).lower() for c in header_row_0):
                    for row in raw_table[1:]:
                        r_clean = [clean_cell_text(c) for c in row]
                        if len(r_clean) >= 6:
                            results["faculty"].append({
                                "sr_no": r_clean[0],
                                "name": r_clean[1] if len(r_clean) > 1 else "",
                                "age": r_clean[2] if len(r_clean) > 2 else "",
                                "designation": r_clean[3] if len(r_clean) > 3 else "",
                                "gender": r_clean[4] if len(r_clean) > 4 else "",
                                "qualification": r_clean[5] if len(r_clean) > 5 else "",
                                "experience_months": r_clean[6] if len(r_clean) > 6 else "",
                                "currently_working": r_clean[7] if len(r_clean) > 7 else "",
                                "joining_date": r_clean[8] if len(r_clean) > 8 else "",
                                "leaving_date": r_clean[9] if len(r_clean) > 9 else "",
                                "association_type": r_clean[10] if len(r_clean) > 10 else "",
                            })

    except Exception as e:
        print(f"[PDF Parser] Error parsing {pdf_path}: {e}")

    return results
