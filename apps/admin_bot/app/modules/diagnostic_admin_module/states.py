"""FSM-состояния diagnostic admin модуля."""

from aiogram.fsm.state import State, StatesGroup


class DiagnosticTranscriptUploadState(StatesGroup):
    waiting_for_document = State()


class DiagnosticResultUploadState(StatesGroup):
    waiting_for_document = State()
