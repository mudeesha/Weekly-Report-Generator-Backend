from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class AIChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[AIChatMessage] = Field(default_factory=list, max_length=10)


class AIChatResponse(BaseModel):
    answer: str
    reports_used: int
    period_start: date
    period_end: date