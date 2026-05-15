"""HTTP-клиент diagnostic admin модуля для работы с backend API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout, FormData

from app.modules.system.config import system_settings

logger = logging.getLogger(__name__)


class DiagnosticAdminBackendClientError(RuntimeError):
    """Базовая ошибка backend-клиента diagnostic admin модуля."""


class DiagnosticAdminBackendNotConfiguredError(DiagnosticAdminBackendClientError):
    """BACKEND_URL не настроен для работы diagnostic admin модуля."""


class DiagnosticAdminBackendUnavailableError(DiagnosticAdminBackendClientError):
    """Backend недоступен по сети или вернул транспортную ошибку."""


class DiagnosticAdminBackendUnexpectedResponseError(DiagnosticAdminBackendClientError):
    """Backend вернул неожиданный ответ, который модуль не умеет обработать."""


@dataclass(slots=True, frozen=True)
class BackendFileUploadResult:
    id: int
    name: str
    link: str
    note: str | None = None


class DiagnosticAdminBackendClient:
    """Тонкий HTTP-клиент для file upload и patch diagnostic run."""

    def __init__(self, session: ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    def build_file_download_url(self, file_id: int) -> str:
        return f"{self._base_url}/files/{file_id}"

    async def upload_transcribation_file(
        self,
        *,
        filename: str,
        content_type: str,
        content: bytes,
        note: str | None = None,
    ) -> BackendFileUploadResult:
        form = FormData()
        form.add_field(
            "file",
            content,
            filename=filename,
            content_type=content_type,
        )
        if note is not None:
            form.add_field("note", note)

        payload = await self._request(
            method="POST",
            path="/files/",
            data=form,
        )
        return BackendFileUploadResult(
            id=int(payload["id"]),
            name=str(payload["name"]),
            link=str(payload["link"]),
            note=payload.get("note"),
        )

    async def attach_transcribation_file(
        self,
        *,
        diagnostic_run_id: int,
        file_id: int,
    ) -> dict[str, Any]:
        return await self._request(
            method="PATCH",
            path=f"/diagnostics/runs/{diagnostic_run_id}/transcribation-file",
            json_payload={"file_id": file_id},
        )

    async def complete_diagnostic_run(
        self,
        *,
        diagnostic_run_id: int,
        result_file_id: int,
    ) -> dict[str, Any]:
        return await self._request(
            method="POST",
            path=f"/diagnostics/runs/{diagnostic_run_id}/complete",
            json_payload={"result_file_id": result_file_id},
        )

    async def _request(
        self,
        *,
        method: str,
        path: str,
        json_payload: dict[str, Any] | None = None,
        data: FormData | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"

        try:
            async with self._session.request(
                method=method,
                url=url,
                json=json_payload,
                data=data,
            ) as response:
                return await self._parse_response(response)
        except DiagnosticAdminBackendClientError:
            raise
        except (ClientError, asyncio.TimeoutError) as exc:
            raise DiagnosticAdminBackendUnavailableError(
                f"Diagnostic admin backend request failed: {exc}"
            ) from exc

    async def _parse_response(self, response: ClientResponse) -> dict[str, Any]:
        if response.status >= 500:
            body = await response.text()
            raise DiagnosticAdminBackendUnavailableError(
                f"Backend returned server error {response.status}: {body}"
            )

        if response.status >= 400:
            body = await response.text()
            raise DiagnosticAdminBackendUnexpectedResponseError(
                f"Backend returned unexpected status {response.status}: {body}"
            )

        try:
            payload = await response.json()
        except Exception as exc:
            body = await response.text()
            raise DiagnosticAdminBackendUnexpectedResponseError(
                f"Backend returned invalid JSON: {body}"
            ) from exc

        if not isinstance(payload, dict):
            raise DiagnosticAdminBackendUnexpectedResponseError(
                "Backend JSON payload must be an object."
            )

        return payload


_backend_client: DiagnosticAdminBackendClient | None = None


async def startup_diagnostic_admin_backend_client() -> None:
    """Поднимает process-wide backend client для diagnostic admin модуля."""

    global _backend_client

    if _backend_client is not None:
        return

    base_url = system_settings.backend_api_base_url
    if not base_url:
        logger.warning(
            "Backend URL is not configured; diagnostic admin backend client is disabled."
        )
        return

    timeout = ClientTimeout(total=system_settings.backend_request_timeout)
    session = ClientSession(timeout=timeout)
    _backend_client = DiagnosticAdminBackendClient(session=session, base_url=base_url)
    logger.info("Diagnostic admin backend client initialized for %s", base_url)


async def shutdown_diagnostic_admin_backend_client() -> None:
    """Закрывает process-wide backend client diagnostic admin модуля."""

    global _backend_client

    if _backend_client is None:
        return

    await _backend_client._session.close()
    _backend_client = None


def get_diagnostic_admin_backend_client() -> DiagnosticAdminBackendClient:
    """Возвращает активный backend client diagnostic admin модуля."""

    if _backend_client is None:
        if not system_settings.backend_api_base_url:
            raise DiagnosticAdminBackendNotConfiguredError(
                "BACKEND_URL is not configured for diagnostic admin module."
            )
        raise DiagnosticAdminBackendUnavailableError(
            "Diagnostic admin backend client is not initialized."
        )
    return _backend_client
