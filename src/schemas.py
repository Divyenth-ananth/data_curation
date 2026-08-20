from typing import Optional, List
from pydantic import BaseModel, Field


class RankingRecord(BaseModel):
    institute_id: str
    institute_name: str
    city: str
    state: str
    score: Optional[float] = None
    rank: str
    rank_band: Optional[str] = "1-100"
    tlr: Optional[float] = None
    rpc: Optional[float] = None
    go: Optional[float] = None
    oi: Optional[float] = None
    perception: Optional[float] = None
    pdf_url: Optional[str] = None


class IntakeRecord(BaseModel):
    institute_id: str
    institute_name: str
    program: str
    intake_2023_24: Optional[int] = None
    intake_2022_23: Optional[int] = None
    intake_2021_22: Optional[int] = None
    intake_2020_21: Optional[int] = None
    intake_2019_20: Optional[int] = None
    intake_2018_19: Optional[int] = None


class DemographicsRecord(BaseModel):
    institute_id: str
    institute_name: str
    program: str
    male_students: Optional[int] = None
    female_students: Optional[int] = None
    total_students: Optional[int] = None
    within_state: Optional[int] = None
    outside_state: Optional[int] = None
    outside_country: Optional[int] = None
    economically_backward: Optional[int] = None
    socially_challenged: Optional[int] = None
    reimbursement_govt: Optional[int] = None
    reimbursement_institution: Optional[int] = None
    reimbursement_private: Optional[int] = None
    no_reimbursement: Optional[int] = None


class PlacementRecord(BaseModel):
    institute_id: str
    institute_name: str
    program: str
    academic_year: str
    first_year_intake: Optional[int] = None
    first_year_admitted: Optional[int] = None
    lateral_admitted: Optional[int] = None
    graduating_stipulated_time: Optional[int] = None
    placed_students: Optional[int] = None
    median_salary_raw: Optional[str] = None
    median_salary_inr: Optional[float] = None
    selected_higher_studies: Optional[int] = None


class PhDRecord(BaseModel):
    institute_id: str
    institute_name: str
    full_time_pursuing: Optional[int] = None
    part_time_pursuing: Optional[int] = None
    phd_graduated_2023_24_full_time: Optional[int] = None
    phd_graduated_2022_23_full_time: Optional[int] = None
    phd_graduated_2021_22_full_time: Optional[int] = None
    phd_graduated_2023_24_part_time: Optional[int] = None
    phd_graduated_2022_23_part_time: Optional[int] = None
    phd_graduated_2021_22_part_time: Optional[int] = None


class FinancialExpenditureRecord(BaseModel):
    institute_id: str
    institute_name: str
    expenditure_type: str  # "Capital Expenditure" or "Operational Expenditure"
    item_description: str
    year_2023_24_inr: Optional[float] = None
    year_2022_23_inr: Optional[float] = None
    year_2021_22_inr: Optional[float] = None
    year_2023_24_raw: Optional[str] = None
    year_2022_23_raw: Optional[str] = None
    year_2021_22_raw: Optional[str] = None


class ProjectConsultancyRecord(BaseModel):
    institute_id: str
    institute_name: str
    category: str  # "Sponsored Research Projects" or "Consultancy Projects"
    metric: str    # "Total Projects", "Funding Agencies / Client Orgs", "Amount INR"
    year_2023_24: Optional[str] = None
    year_2022_23: Optional[str] = None
    year_2021_22: Optional[str] = None


class FacultyRecord(BaseModel):
    institute_id: str
    institute_name: str
    sr_no: Optional[str] = None
    name: str
    age: Optional[int] = None
    designation: Optional[str] = None
    gender: Optional[str] = None
    qualification: Optional[str] = None
    experience_months: Optional[int] = None
    currently_working: Optional[str] = None
    joining_date: Optional[str] = None
    leaving_date: Optional[str] = None
    association_type: Optional[str] = None
