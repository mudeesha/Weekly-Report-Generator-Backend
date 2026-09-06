from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


ActivityType = Literal["REPORT_SUBMITTED", "CHANGES_REQUESTED", "REPORT_APPROVED"]


class DashboardSummaryResponse(BaseModel):
    total_reports: int
    draft_reports: int
    submitted_reports: int
    needs_correction_reports: int
    approved_reports: int
    total_spent_hours: float


class StatusDistributionResponse(BaseModel):
    status: str
    count: int


class ProjectHoursResponse(BaseModel):
    project_id: int
    project_name: str
    spent_hours: float


class DashboardActivityResponse(BaseModel):
    activity_type: ActivityType
    message: str
    report_id: int
    version_number: int
    user_id: int
    user_name: str
    reviewer_id: int | None = None
    reviewer_name: str | None = None
    week_start: date
    created_at: datetime