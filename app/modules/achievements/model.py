from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportAchievement(Base):
    __tablename__ = "report_achievements"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    report_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "report_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_key_achievement: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )