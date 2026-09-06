from decimal import Decimal

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportTask(Base):
    __tablename__ = "report_tasks"

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

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    section: Mapped[str] = mapped_column(
        Enum(
            "THIS_WEEK",
            "NEXT_WEEK",
            name="task_section",
        ),
        nullable=False,
    )

    task_type: Mapped[str] = mapped_column(
        Enum(
            "DEVELOPMENT",
            "TESTING",
            "MEETINGS",
            "DOCUMENTATION",
            "SUPPORT",
            "RESEARCH",
            "OTHER",
            name="task_type",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    priority: Mapped[str | None] = mapped_column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
            name="task_priority",
        ),
        nullable=True,
    )

    planned_percent: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    actual_percent: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        Enum(
            "NOT_STARTED",
            "IN_PROGRESS",
            "COMPLETED",
            "BLOCKED",
            name="task_status",
        ),
        nullable=True,
    )

    planned_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    spent_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )