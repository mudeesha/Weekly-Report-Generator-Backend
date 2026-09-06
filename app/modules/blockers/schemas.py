from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


BlockerStatus = Literal[
    "OPEN",
    "RESOLVED",
]


class ReportBlockerRequest(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    status: BlockerStatus = "OPEN"

    is_key_issue: bool = False


class ReportBlockerResponse(ReportBlockerRequest):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )