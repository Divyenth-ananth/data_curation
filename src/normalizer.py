import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.schemas import (
    RankingRecord,
    IntakeRecord,
    DemographicsRecord,
    PlacementRecord,
    FinancialExpenditureRecord,
    ProjectConsultancyRecord,
    FacultyRecord,
)


def parse_int_safe(val: Any) -> Optional[int]:
    if val is None:
        return None
    s = re.sub(r"[^\d]", "", str(val))
    return int(s) if s else None


def parse_currency_safe(val: Any) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    # Match leading numbers before word descriptions (e.g., "1700000(Seventeen Lakhs)" or "26,87,46,540 (Twenty...")
    match = re.match(r"^[\s]*([\d,]+)", s)
    if match:
        clean_num = match.group(1).replace(",", "")
        try:
            return float(clean_num)
        except ValueError:
            return None
    return None


def normalize_all_data(rankings: List[Dict[str, Any]], parsed_pdf_results: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Normalizes extracted data from scraping and PDF parsing into 7 clean relational DataFrames.
    """
    # 1. Master Rankings DataFrame
    rankings_rows = []
    for r in rankings:
        rec = RankingRecord(
            institute_id=r.get("institute_id", ""),
            institute_name=r.get("institute_name", ""),
            city=r.get("city", ""),
            state=r.get("state", ""),
            score=r.get("score"),
            rank=str(r.get("rank", "")),
            rank_band=r.get("rank_band", "1-100"),
            tlr=r.get("tlr"),
            rpc=r.get("rpc"),
            go=r.get("go"),
            oi=r.get("oi"),
            perception=r.get("perception"),
            pdf_url=r.get("pdf_url"),
        )
        rankings_rows.append(rec.model_dump())
    df_rankings = pd.DataFrame(rankings_rows)

    # 2. Sanctioned Intake DataFrame
    intake_rows = []
    # 3. Demographics DataFrame
    demographics_rows = []
    # 4. Placements DataFrame
    placements_rows = []
    # 5. Financial Expenditures DataFrame
    financial_rows = []
    # 6. Sponsored & Consultancy DataFrame
    projects_rows = []
    # 7. Faculty DataFrame
    faculty_rows = []

    for item in parsed_pdf_results:
        inst_id = item.get("institute_id", "")
        inst_name = item.get("institute_name", "")

        # Process Intake
        for r in item.get("intake", []):
            rec = IntakeRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                program=r.get("program", ""),
                intake_2023_24=parse_int_safe(r.get("intake_2023_24")),
                intake_2022_23=parse_int_safe(r.get("intake_2022_23")),
                intake_2021_22=parse_int_safe(r.get("intake_2021_22")),
                intake_2020_21=parse_int_safe(r.get("intake_2020_21")),
                intake_2019_20=parse_int_safe(r.get("intake_2019_20")),
                intake_2018_19=parse_int_safe(r.get("intake_2018_19")),
            )
            intake_rows.append(rec.model_dump())

        # Process Demographics
        for r in item.get("demographics", []):
            rec = DemographicsRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                program=r.get("program", ""),
                male_students=parse_int_safe(r.get("male_students")),
                female_students=parse_int_safe(r.get("female_students")),
                total_students=parse_int_safe(r.get("total_students")),
                within_state=parse_int_safe(r.get("within_state")),
                outside_state=parse_int_safe(r.get("outside_state")),
                outside_country=parse_int_safe(r.get("outside_country")),
                economically_backward=parse_int_safe(r.get("economically_backward")),
                socially_challenged=parse_int_safe(r.get("socially_challenged")),
                reimbursement_govt=parse_int_safe(r.get("reimbursement_govt")),
                reimbursement_institution=parse_int_safe(r.get("reimbursement_institution")),
                reimbursement_private=parse_int_safe(r.get("reimbursement_private")),
                no_reimbursement=parse_int_safe(r.get("no_reimbursement")),
            )
            demographics_rows.append(rec.model_dump())

        # Process Placements
        for r in item.get("placements", []):
            salary_raw = r.get("median_salary_raw", "")
            rec = PlacementRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                program=r.get("program", ""),
                academic_year=r.get("academic_year", ""),
                first_year_intake=parse_int_safe(r.get("first_year_intake")),
                first_year_admitted=parse_int_safe(r.get("first_year_admitted")),
                lateral_admitted=parse_int_safe(r.get("lateral_admitted")),
                graduating_stipulated_time=parse_int_safe(r.get("graduating_stipulated_time")),
                placed_students=parse_int_safe(r.get("placed_students")),
                median_salary_raw=salary_raw,
                median_salary_inr=parse_currency_safe(salary_raw),
                selected_higher_studies=parse_int_safe(r.get("selected_higher_studies")),
            )
            placements_rows.append(rec.model_dump())

        # Process Capital Expenditure
        for r in item.get("capital_expenditure", []):
            rec = FinancialExpenditureRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                expenditure_type="Capital Expenditure",
                item_description=r.get("item_description", ""),
                year_2023_24_inr=parse_currency_safe(r.get("year_2023_24_raw")),
                year_2022_23_inr=parse_currency_safe(r.get("year_2022_23_raw")),
                year_2021_22_inr=parse_currency_safe(r.get("year_2021_22_raw")),
                year_2023_24_raw=r.get("year_2023_24_raw"),
                year_2022_23_raw=r.get("year_2022_23_raw"),
                year_2021_22_raw=r.get("year_2021_22_raw"),
            )
            financial_rows.append(rec.model_dump())

        # Process Operational Expenditure
        for r in item.get("operational_expenditure", []):
            rec = FinancialExpenditureRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                expenditure_type="Operational Expenditure",
                item_description=r.get("item_description", ""),
                year_2023_24_inr=parse_currency_safe(r.get("year_2023_24_raw")),
                year_2022_23_inr=parse_currency_safe(r.get("year_2022_23_raw")),
                year_2021_22_inr=parse_currency_safe(r.get("year_2021_22_raw")),
                year_2023_24_raw=r.get("year_2023_24_raw"),
                year_2022_23_raw=r.get("year_2022_23_raw"),
                year_2021_22_raw=r.get("year_2021_22_raw"),
            )
            financial_rows.append(rec.model_dump())

        # Process Sponsored Research
        for r in item.get("sponsored_research", []):
            rec = ProjectConsultancyRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                category="Sponsored Research Projects",
                metric=r.get("metric", ""),
                year_2023_24=r.get("year_2023_24"),
                year_2022_23=r.get("year_2022_23"),
                year_2021_22=r.get("year_2021_22"),
            )
            projects_rows.append(rec.model_dump())

        # Process Consultancy
        for r in item.get("consultancy", []):
            rec = ProjectConsultancyRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                category="Consultancy Projects",
                metric=r.get("metric", ""),
                year_2023_24=r.get("year_2023_24"),
                year_2022_23=r.get("year_2022_23"),
                year_2021_22=r.get("year_2021_22"),
            )
            projects_rows.append(rec.model_dump())

        # Process Faculty
        for r in item.get("faculty", []):
            rec = FacultyRecord(
                institute_id=inst_id,
                institute_name=inst_name,
                sr_no=r.get("sr_no"),
                name=r.get("name", ""),
                age=parse_int_safe(r.get("age")),
                designation=r.get("designation"),
                gender=r.get("gender"),
                qualification=r.get("qualification"),
                experience_months=parse_int_safe(r.get("experience_months")),
                currently_working=r.get("currently_working"),
                joining_date=r.get("joining_date"),
                leaving_date=r.get("leaving_date"),
                association_type=r.get("association_type"),
            )
            faculty_rows.append(rec.model_dump())

    return {
        "Rankings_Master": df_rankings,
        "Sanctioned_Intake": pd.DataFrame(intake_rows),
        "Student_Demographics": pd.DataFrame(demographics_rows),
        "Placements_and_Salaries": pd.DataFrame(placements_rows),
        "Financial_Expenditures": pd.DataFrame(financial_rows),
        "Research_and_Consultancy": pd.DataFrame(projects_rows),
        "Faculty_Roster": pd.DataFrame(faculty_rows),
    }
