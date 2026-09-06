from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.achievements.schemas import ReportAchievementRequest
from app.modules.blockers.schemas import ReportBlockerRequest
from app.modules.reviews.schemas import ReviewResponse
from app.modules.tasks.schemas import ReportTaskRequest
from app.modules.versions.schemas import ReportVersionResponse


ReportStatus = Literal["DRAFT", "SUBMITTED", "NEEDS_CORRECTION", "APPROVED"]


class ReportCreateRequest(BaseModel):
    week_start: date
    notes: str | None = None
    tasks: list[ReportTaskRequest] = Field(default_factory=list)
    blockers: list[ReportBlockerRequest] = Field(default_factory=list)
    achievements: list[ReportAchievementRequest] = Field(default_factory=list)


class ReportUpdateRequest(BaseModel):
    notes: str | None = None
    tasks: list[ReportTaskRequest] | None = None
    blockers: list[ReportBlockerRequest] | None = None
    achievements: list[ReportAchievementRequest] | None = None


class ReportListItemResponse(BaseModel):
    id: int
    user_id: int
    week_start: date
    week_end: date
    due_at: datetime
    status: ReportStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedReportsResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[ReportListItemResponse]


class ReportResponse(BaseModel):
    id: int
    user_id: int
    week_start: date
    week_end: date
    due_at: datetime
    status: ReportStatus
    created_at: datetime
    updated_at: datetime
    current_version: ReportVersionResponse
    latest_review: ReviewResponse | None = None

    model_config = ConfigDict(from_attributes=True)