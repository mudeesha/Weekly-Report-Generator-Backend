from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReviewAction = Literal["APPROVE", "REQUEST_CHANGES"]


class RequestChangesRequest(BaseModel):
    comment: str = Field(min_length=2, max_length=2000)


class ReviewResponse(BaseModel):
    id: int
    report_version_id: int
    reviewer_id: int
    action: ReviewAction
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)