from typing import Any, Optional

import httpx
from pydantic import BaseModel
from openprinttag_web_api.integrations.printer.bgcode import (
    GcodeMetadata,
    parse_gcode_header,
)


class JobFileRefs(BaseModel):
    """File references in job response."""

    download: str
    icon: Optional[str] = None
    thumbnail: Optional[str] = None


class JobFile(BaseModel):
    """File info in job response."""

    display_name: str
    refs: JobFileRefs


class JobResponse(BaseModel):
    """PrusaLink /api/v1/job response."""

    id: int
    progress: float
    file: JobFile


class PrusaLinkClient:
    """Async client for PrusaLink API."""

    def __init__(self, host: str, api_key: str, port: int = 80):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.headers = {"X-Api-Key": api_key}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "PrusaLinkClient":
        self._client = httpx.AsyncClient(headers=self.headers, timeout=10.0)
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager."
            )
        return self._client

    async def get_status(self) -> dict:
        """Get printer status."""
        _response = await self.client.get(f"{self.base_url}/api/v1/status")
        _response.raise_for_status()
        return _response.json()

    async def get_job(self) -> Optional[JobResponse]:
        """Get current job info."""
        _response = await self.client.get(f"{self.base_url}/api/v1/job")
        if _response.status_code == 204:
            return None
        _response.raise_for_status()
        return JobResponse.model_validate(_response.json())

    async def get_file_info(self, storage: str, filename: str) -> dict:
        """Get file info from PrusaLink API.

        Args:
            storage: Storage location (e.g., 'usb', 'local')
            filename: Display name of the file

        Returns:
            File info dict with 'meta' containing filament data
        """
        _response = await self.client.get(
            f"{self.base_url}/api/v1/files/{storage}/{filename}"
        )
        _response.raise_for_status()
        return _response.json()

    async def get_gcode_metadata(
        self, file_path: str, header_size: int = 8192
    ) -> GcodeMetadata | None:
        """Fetch and parse gcode metadata (only downloads header)."""
        _headers: dict[str, Any] = {
            **self.headers,
            "Range": f"bytes=0-{header_size - 1}",
        }
        _response: httpx.Response = await self.client.get(
            f"{self.base_url}{file_path}", headers=_headers
        )
        _response.raise_for_status()
        return parse_gcode_header(_response.content)
