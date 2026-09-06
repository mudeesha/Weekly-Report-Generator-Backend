from pydantic import BaseModel, ConfigDict, Field


class ReportAchievementRequest(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    is_key_achievement: bool = False


class ReportAchievementResponse(ReportAchievementRequest):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )