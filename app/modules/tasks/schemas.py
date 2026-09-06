from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskSection = Literal[
    "THIS_WEEK",
    "NEXT_WEEK",
]

TaskType = Literal[
    "DEVELOPMENT",
    "TESTING",
    "MEETINGS",
    "DOCUMENTATION",
    "SUPPORT",
    "RESEARCH",
    "OTHER",
]

TaskPriority = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]

TaskStatus = Literal[
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "BLOCKED",
]


class ReportTaskRequest(BaseModel):
    project_id: int

    section: TaskSection

    task_type: TaskType

    name: str = Field(
        min_length=2,
        max_length=255,
    )

    priority: TaskPriority | None = None

    planned_percent: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    actual_percent: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    status: TaskStatus | None = None

    planned_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    spent_hours: Decimal | None = Field(
        default=None,
        ge=0,
    )

    output: str | None = None


class ReportTaskResponse(ReportTaskRequest):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )