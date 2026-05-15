from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.base_diagnostic_module.schemas import DiagnosticRunRead


class InvisibleDiagnosticCreate(BaseModel):
    user_id: int
    voice_file_id: int
    description: str | None = None


class InvisibleDiagnosticRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    diagnostic_run_id: int
    diagnostic_run: DiagnosticRunRead
