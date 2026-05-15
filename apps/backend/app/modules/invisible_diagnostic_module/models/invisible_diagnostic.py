from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.system import Base, TimestampMixin

if TYPE_CHECKING:
    from app.modules.base_diagnostic_module import DiagnosticRun


class InvisibleDiagnostic(Base, TimestampMixin):
    diagnostic_run_id: Mapped[int] = mapped_column(
        ForeignKey("diagnosticrun.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    diagnostic_run: Mapped["DiagnosticRun"] = relationship(lazy="selectin")
