from typing import Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_applications: int
    total_loan_amount: float
    low_risk: int
    medium_risk: int
    high_risk: int
    average_default_probability: float
    blockchain_registered: int
    verified_records: int


class DateRangeFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
