class DiagnosticRunStatus:
    CREATED = "created"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def values(cls) -> set[str]:
        return {
            cls.CREATED,
            cls.COMPLETED,
            cls.FAILED,
        }
