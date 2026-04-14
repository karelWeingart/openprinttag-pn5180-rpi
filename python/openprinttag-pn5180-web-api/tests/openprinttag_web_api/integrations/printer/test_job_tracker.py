import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_mock

from openprinttag_web_api.integrations.printer.job_tracker import (
    _jobs as job_tracker_jobs,
    JobWatcherState,
    get_gcode_metadata_for_jobs,
    watch_jobs,
    GcodeMetadata,
)
from openprinttag_web_api.integrations.printer.prusalink.client import (
    JobResponse,
    JobFile,
    JobFileRefs,
)

# from openprinttag_web_api.test_helpers import fake_async_sleep, set_async_sleep_max_call


@pytest.fixture
def mock_sleep(mocker: pytest_mock.plugin.MockerFixture) -> AsyncMock:
    return mocker.patch(
        "openprinttag_web_api.integrations.printer.job_tracker.asyncio.sleep"
    )


@pytest.fixture
def mock_client(mocker: pytest_mock.plugin.MockerFixture) -> AsyncMock:
    return mocker.AsyncMock()


_SUCCESS_METADATA = GcodeMetadata(
    filament_type="PLA",
    filament_used_g=10.0,
    estimated_print_time_s=3600,
)

_job_response = JobResponse(
    id=24,
    progress=0.75,
    file=JobFile(
        display_name="benchy.gcode",
        refs=JobFileRefs(download="/usb/benchy.bgcode"),
    ),
)

_second_job_response = JobResponse(
    id=25,
    progress=0.75,
    file=JobFile(
        display_name="benchy.gcode",
        refs=JobFileRefs(download="/usb/benchy.bgcode"),
    ),
)


@pytest.mark.anyio
async def test_get_gcode_metadata_for_jobs() -> None:
    """Test get_gcode_metadata_for_jobs function."""
    job_tracker_jobs.clear()
    job_tracker_jobs.update(
        {
            1: JobWatcherState(
                job_id=1,
                gcode_download_path="/usb/test.gcode",
                file_name="test.gcode",
                gcode_downloaded=True,
            )
        }
    )
    _client = AsyncMock()
    _client.get_gcode_metadata.return_value = _SUCCESS_METADATA
    try:
        _completed: int = await get_gcode_metadata_for_jobs(
            _client, max_gcode_download_attempts=3
        )
        assert _completed == 0
    finally:
        job_tracker_jobs.clear()


@pytest.mark.anyio
@pytest.mark.parametrize("max_attempts, number_of_failures", [(4, 4), (5, 3), (2, 3)])
async def test_get_gcode_metadata_after_finished_printing(
    max_attempts: int, number_of_failures: int
) -> None:
    """Test that metadata is downloaded after a number of failed attempts."""
    job_tracker_jobs.clear()
    job_tracker_jobs.update(
        {
            1: JobWatcherState(
                job_id=1,
                gcode_download_path="/usb/test.gcode",
                file_name="test.gcode",
                gcode_downloaded=False,
                is_printing=False,
            )
        }
    )
    _client = AsyncMock()
    _client.get_gcode_metadata.side_effect = [
        httpx.HTTPError("fail")
    ] * number_of_failures + [_SUCCESS_METADATA]
    try:
        for _attempt in range(number_of_failures):
            _completed = await get_gcode_metadata_for_jobs(
                _client, max_gcode_download_attempts=max_attempts
            )

            if _attempt >= max_attempts:
                # Last attempt after max_attempts is reached for job_state is made
                # and the job_state is removed from the job_tracker_jobs dict.
                assert job_tracker_jobs.get(1) is None

            else:
                # Attempts within max_attempts should not complete the metadata download
                # and should update the job_state with the number of attempts.
                _job_state: JobWatcherState = job_tracker_jobs[1]
                assert _attempt == _job_state.gcode_download_attempts - 1
                assert _completed == 0
                assert _job_state.gcode_downloaded is False

        if number_of_failures <= max_attempts:
            # Successful attempt after failures within max_attempts.
            _completed = await get_gcode_metadata_for_jobs(
                _client, max_gcode_download_attempts=max_attempts
            )
            _job_state = job_tracker_jobs[1]
            assert _completed == 1
            assert _job_state.gcode_downloaded is True
            assert _job_state.metadata
            assert _job_state.metadata.filament_type == "PLA"
    finally:
        job_tracker_jobs.clear()


@pytest.mark.anyio
async def test_get_gcode_metadata_during_printing() -> None:
    """Test that metadata is not downloaded during printing."""
    job_tracker_jobs.clear()
    job_tracker_jobs.update(
        {
            1: JobWatcherState(
                job_id=1,
                gcode_download_path="/usb/test.gcode",
                file_name="test.gcode",
                gcode_downloaded=False,
                is_printing=True,
            )
        }
    )
    _client = AsyncMock()
    _max_attempts = 3
    _side_effects = [httpx.HTTPError("fail")] * (_max_attempts + 1) + [
        _SUCCESS_METADATA
    ]
    _client.get_gcode_metadata.side_effect = _side_effects
    try:
        _job_state: JobWatcherState = None
        _completed: int = 0
        for _ in range(len(_side_effects)):
            assert _completed == 0
            _completed = await get_gcode_metadata_for_jobs(
                _client, max_gcode_download_attempts=_max_attempts
            )
            _job_state = job_tracker_jobs.get(1)
            assert _job_state.gcode_download_attempts == 0
        assert _completed == 1

        assert _job_state.gcode_downloaded is True
        assert _job_state.is_printing is True
        assert _job_state.metadata
        assert _job_state.metadata.filament_type == "PLA"
    finally:
        job_tracker_jobs.clear()


@pytest.mark.anyio
async def test_watch_jobs_not_downloaded(
    mocker: pytest_mock.plugin.MockerFixture,
    mock_sleep: AsyncMock,
    mock_client: AsyncMock,
) -> None:
    """Test that watch_jobs yields a CompletedJobDto when a job finishes."""
    job_tracker_jobs.clear()

    mock_client.get_job.side_effect = [_job_response, Exception("not found"), None]
    _mock_get_gcode_metadata = mocker.patch(
        "openprinttag_web_api.integrations.printer.job_tracker.get_gcode_metadata_for_jobs"
    )
    _mock_get_gcode_metadata.side_effect = [Exception("test error"), 0, 0]

    mock_sleep.side_effect = [None, None, asyncio.CancelledError("test")]

    try:
        _watcher = watch_jobs(mock_client, interval=1.0, max_gcode_download_attempts=3)
        _ = await _watcher.__anext__()

    except asyncio.CancelledError:
        print("Test completed with CancelledError as expected.")
    finally:
        assert len(job_tracker_jobs) == 1
        _job_state = job_tracker_jobs.get(24)
        assert _job_state
        assert _job_state.is_printing is False
        assert _job_state.gcode_downloaded is False
        assert _job_state.metadata is None
        assert _mock_get_gcode_metadata.call_count == 2
        job_tracker_jobs.clear()


@pytest.mark.anyio
async def test_watch_jobs_fully_completed(
    mock_sleep: AsyncMock, mock_client: AsyncMock
) -> None:
    """Test that watch_jobs yields a CompletedJobDto when a job finishes."""
    job_tracker_jobs.clear()

    mock_client.get_job.side_effect = [_job_response, None, None, None]
    mock_client.get_gcode_metadata.side_effect = [None, None, _SUCCESS_METADATA, None]
    mock_sleep.side_effect = [None, None, None, asyncio.CancelledError("test")]

    try:
        _watcher = watch_jobs(mock_client, interval=1.0, max_gcode_download_attempts=3)
        _ = await _watcher.__anext__()

    except asyncio.CancelledError:
        print("Test completed with CancelledError as expected.")
    finally:
        assert len(job_tracker_jobs) == 0
        _job_state = job_tracker_jobs.get(24, None)
        assert not _job_state
        job_tracker_jobs.clear()


@pytest.mark.anyio
async def test_watch_jobs_never_downloaded_job(
    mock_sleep: AsyncMock, mock_client: AsyncMock
) -> None:
    """Test that watch_jobs yields a CompletedJobDto when a job finishes."""
    job_tracker_jobs.clear()

    mock_client.get_job.side_effect = [_job_response, None, None, None]
    mock_client.get_gcode_metadata.side_effect = [None, None, None, None]
    mock_sleep.side_effect = [None, None, None, asyncio.CancelledError("test")]

    try:
        _watcher = watch_jobs(mock_client, interval=1.0, max_gcode_download_attempts=2)
        _ = await _watcher.__anext__()

    except asyncio.CancelledError:
        print("Test completed with CancelledError as expected.")
    finally:
        assert len(job_tracker_jobs) == 0
        _job_state = job_tracker_jobs.get(24, None)
        assert not _job_state
        job_tracker_jobs.clear()


@pytest.mark.anyio
async def test_watch_jobs_another_job(
    mock_sleep: AsyncMock, mock_client: AsyncMock
) -> None:
    """Test that watch_jobs yields a CompletedJobDto when a job finishes."""
    job_tracker_jobs.clear()

    mock_client.get_job.side_effect = [_job_response, _second_job_response, None, None]
    mock_client.get_gcode_metadata.side_effect = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    mock_sleep.side_effect = [None, None, None, asyncio.CancelledError("test")]

    try:
        _watcher = watch_jobs(mock_client, interval=1.0, max_gcode_download_attempts=4)
        _ = await _watcher.__anext__()

    except asyncio.CancelledError:
        print("Test completed with CancelledError as expected.")
    finally:
        assert len(job_tracker_jobs) == 2
        _job_state = job_tracker_jobs.get(24, None)
        assert _job_state
        assert _job_state.is_printing is False
        assert _job_state.gcode_downloaded is False
        _job_state = job_tracker_jobs.get(25, None)
        assert _job_state
        assert _job_state.is_printing is False
        assert _job_state.gcode_downloaded is False
        job_tracker_jobs.clear()
