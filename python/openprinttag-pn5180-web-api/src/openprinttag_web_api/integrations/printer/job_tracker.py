import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional

import httpx
from openprinttag_shared.models.dto import CompletedJobDto
from openprinttag_web_api.integrations.printer.bgcode import (
    GcodeMetadata,
    calculate_filament_used,
)
from openprinttag_web_api.integrations.printer.prusalink.client import (
    PrusaLinkClient,
    JobResponse,
)


@dataclass
class JobWatcherState:
    """State for tracking current job."""

    job_id: int
    gcode_download_path: str
    gcode_downloaded: bool = False
    gcode_download_attempts: int = 0
    is_printing: bool = True
    metadata: Optional[GcodeMetadata] = None
    file_name: Optional[str] = None    
    last_progress: float = 0.0

    def create_completed_job(self, end_reason: str) -> CompletedJobDto:
        """Create CompletedJobDto from current state."""

        usage = calculate_filament_used(self.metadata, self.last_progress)
        return CompletedJobDto(
            job_id=self.job_id,
            file_name=self.file_name or "unknown",
            filament_type=self.metadata.filament_type,
            total_filament_g=self.metadata.filament_used_g,
            used_filament_g=usage.get("used_g"),
            final_progress=self.last_progress,
            end_reason=end_reason,
        )

_jobs: dict[int, JobWatcherState] = {}

def add_job_to_watchlist(
    job: JobResponse
) -> None:
    """add job to watchlist otherwise update progress 
        and check for completion.
    """
    if job.id not in _jobs:
        # New job started
        _new_job = JobWatcherState(
            job_id=job.id,
            file_name=job.file.display_name,
            gcode_download_path=job.file.refs.download,
        )
        for s in _jobs.values():
            s.is_printing = False
        _jobs[job.id] = _new_job
    else:
        # Update progress for existing job
        _job_state = _jobs[job.id]
        _job_state.last_progress = job.progress

def finish_job_in_watchlist() -> None:
    """Check watchlist for any job that was printing but is no longer active."""
    for _job in _jobs.values():
        if _job.is_printing:
            _job.is_printing = False

def remove_job_from_watchlist(job_id: int) -> None:
    """Remove job from watchlist."""
    if job_id in _jobs:
        del _jobs[job_id]

async def get_gcode_metadata_for_jobs(client: PrusaLinkClient, max_gcode_download_attempts: int) -> int:
    """Download gcode metadata for any job that hasn't had it downloaded yet."""
    _downloaded_count = 0
    for _job in _jobs.values():
        if not _job.gcode_downloaded:
            try:
                _metadata = await client.get_gcode_metadata(_job.gcode_download_path)
                if _metadata:
                    _job.metadata = _metadata
                    _job.gcode_downloaded = True
                    _downloaded_count += 1
            except httpx.HTTPError as e:
                if not _job.is_printing and _job.gcode_download_attempts >= max_gcode_download_attempts:
                    print(f"Max gcode download attempts reached for job {_job.job_id}. Skipping metadata.")
                    remove_job_from_watchlist(_job.job_id)
                elif not _job.is_printing:
                    _job.gcode_download_attempts += 1
                print(f"HTTP error while downloading gcode metadata: {e}")
    return _downloaded_count

async def watch_jobs(
    client: PrusaLinkClient,
    interval: float = 20.0,
    max_gcode_download_attempts: int = 20,
) -> AsyncIterator[CompletedJobDto]:
    """Watch for print jobs and yield when they complete.

    Yields CompletedJobDto when a job finishes (completed, canceled, stopped).

    Args:
        client: Initialized PrusaLinkClient instance
        interval: Polling interval in seconds

    Yields:
        CompletedJobDto with final consumption data
    """

    while True:
        try:
            _job: JobResponse | None = await client.get_job()

            if _job:
                add_job_to_watchlist(_job)
            else:
                finish_job_in_watchlist()

            _gcode_downloaded = await get_gcode_metadata_for_jobs(client, max_gcode_download_attempts)

            if _gcode_downloaded:
                _completed_jobs: list[CompletedJobDto | None] = [
                    _job.create_completed_job(end_reason="completed")
                    for _job in _jobs.values()
                    if not _job.is_printing and _job.metadata is not None
                ]
                for _completed_job in _completed_jobs:
                    yield _completed_job
                    remove_job_from_watchlist(_completed_job.job_id)
                print(f"Downloaded metadata for {_gcode_downloaded} job(s).")


        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)
