from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.achievements.schemas import ReportAchievementResponse
from app.modules.blockers.schemas import ReportBlockerResponse
from app.modules.reviews.schemas import ReviewResponse
from app.modules.tasks.schemas import ReportTaskResponse


class ReportVersionResponse(BaseModel):
    id: int
    version_number: int
    notes: str | None
    submitted_at: datetime | None
    tasks: list[ReportTaskResponse] = Field(default_factory=list)
    blockers: list[ReportBlockerResponse] = Field(default_factory=list)
    achievements: list[ReportAchievementResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReportVersionHistoryResponse(ReportVersionResponse):
    reviews: list[ReviewResponse] = Field(default_factory=list)