from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.base_diagnostic_module.schemas import DiagnosticRunRead


class DefaultDiagnosticCreate(BaseModel):
    user_id: int
    voice_file_id: int
    description: str | None = None


class DefaultDiagnosticRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    diagnostic_run_id: int
    diagnostic_run: DiagnosticRunRead
