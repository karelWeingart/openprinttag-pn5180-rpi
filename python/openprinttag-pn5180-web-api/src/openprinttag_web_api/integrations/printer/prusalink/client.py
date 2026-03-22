import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

import httpx
from pydantic import BaseModel
from openprinttag_shared.models.dto import CompletedJobDto
from openprinttag_web_api.integrations.printer.bgcode import (
    GcodeMetadata,
    parse_gcode_header,
    calculate_filament_used,
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
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    async def get_status(self) -> dict:
        """Get printer status."""
        response = await self.client.get(f"{self.base_url}/api/v1/status")
        response.raise_for_status()
        return response.json()

    async def get_job(self) -> Optional[JobResponse]:
        """Get current job info."""
        response = await self.client.get(f"{self.base_url}/api/v1/job")
        if response.status_code == 204:  # No job
            return None
        response.raise_for_status()
        return JobResponse.model_validate(response.json())

    async def get_file_info(self, storage: str, filename: str) -> dict:
        """Get file metadata from PrusaLink API.
        
        Args:
            storage: Storage location (e.g., 'usb', 'local')
            filename: Display name of the file
            
        Returns:
            File info dict with 'meta' containing filament data
        """
        response = await self.client.get(f"{self.base_url}/api/v1/files/{storage}/{filename}")
        response.raise_for_status()
        return response.json()

    async def get_file_metadata(self, file_path: str, header_size: int = 4096) -> GcodeMetadata:
        """Fetch and parse gcode metadata (only downloads header)."""
        headers = {**self.headers, "Range": f"bytes=0-{header_size - 1}"}
        response = await self.client.get(f"{self.base_url}{file_path}", headers=headers)
        response.raise_for_status()
        return parse_gcode_header(response.content)


@dataclass
class JobWatcherState:
    """State for tracking current job."""
    
    job_id: Optional[int] = None
    metadata: Optional[GcodeMetadata] = None
    file_name: Optional[str] = None
    last_progress: float = 0.0

    def reset(self) -> None:
        """Reset state after job ends."""
        self.job_id = None
        self.metadata = None
        self.file_name = None
        self.last_progress = 0.0
    
    def init_job(self, job: JobResponse, metadata: GcodeMetadata) -> None:
        self.job_id = job.id
        self.file_name = job.file.display_name
        self.metadata = metadata

    def create_completed_job(self, end_reason: str) -> Optional[CompletedJobDto]:
        """Create CompletedJobDto from current state."""
        if self.metadata is None:
            return None
        
        usage = calculate_filament_used(self.metadata, self.last_progress)
        return CompletedJobDto(
            job_id=self.job_id or 0,
            file_name=self.file_name or "unknown",
            filament_type=self.metadata.filament_type,
            total_filament_g=self.metadata.filament_used_g,
            used_filament_g=usage.get("used_g"),
            final_progress=self.last_progress,
            end_reason=end_reason,
        )


async def watch_job(
    client: PrusaLinkClient,
    job: JobResponse,
    state: JobWatcherState,
) -> Optional[CompletedJobDto]:
    """Process a single job update.
    
    Args:
        client: PrusaLink client
        job: Job data from API
        state: Current watcher state (modified in place)
        
    Returns:
        CompletedJobDto if a job just ended, None otherwise
    """
    completed_job: Optional[CompletedJobDto] = None
    
    # New job started
    if job.id != state.job_id:
        # If we had a previous job, it ended (replaced by new one)
        if state.job_id is not None and state.metadata:
            completed_job = state.create_completed_job("replaced")
        
        # Fetch metadata by downloading file header
        # Use refs.download path for actual file content (8.3 short name format)
        download_ref = job.file.refs.download
        
        # Use larger header size for reliability
        _metadata: GcodeMetadata = await client.get_file_metadata(download_ref, header_size=16384)
        print(f"Parsed metadata: filament_type={_metadata.filament_type}, filament_used_g={_metadata.filament_used_g}")
        state.init_job(job, _metadata)
    
    state.last_progress = job.progress
    
    # Log progress
    if state.metadata and state.metadata.filament_used_g is not None:
        usage = calculate_filament_used(state.metadata, job.progress)
        print(f"Progress: {job.progress}% | Used: {usage['used_g']:.2f}g / {usage['total_g']:.2f}g")
    elif state.metadata:
        print(f"Progress: {job.progress}% | Filament data not available (filament_used_g={state.metadata.filament_used_g})")
    
    return completed_job


async def watch_jobs(
    client: PrusaLinkClient,
    interval: float = 20.0,
) -> AsyncIterator[CompletedJobDto]:
    """Watch for print jobs and yield when they complete.
    
    Yields CompletedJobDto when a job finishes (completed, canceled, stopped).
    
    Args:
        client: Initialized PrusaLinkClient instance
        interval: Polling interval in seconds
        
    Yields:
        CompletedJobDto with final consumption data
    """
    state = JobWatcherState()

    while True:
        try:
            job: JobResponse | None = await client.get_job()

            if job:
                completed_job = await watch_job(client, job, state)
                if completed_job:
                    yield completed_job
            else:
                if state.job_id:
                    end_reason = "completed" if state.last_progress >= 99.0 else "canceled"
                    completed_job = state.create_completed_job(end_reason)
                    
                    if completed_job:
                        yield completed_job
                    
                    print(f"Job {end_reason}: {state.file_name}")
                    state.reset()

        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)
