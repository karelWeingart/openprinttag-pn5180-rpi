""" Singleton service managing connection to the currently enabled printer. """
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable
import asyncio

from openprinttag_web_api.integrations.printer.prusalink.client import PrusaLinkClient, watch_jobs
from openprinttag_web_api.models.domain import PrinterRecord
from openprinttag_web_api.repositories.printers import PrinterRepository
from openprinttag_web_api.services.filament_tracking import filament_tracking
from openprinttag_web_api.repositories.sqlite.printers import SqlitePrinterRepository


@dataclass
class PrinterConnection:
    """Current active printer connection state."""
    printer: PrinterRecord
    client: PrusaLinkClient
    watcher_task: Optional[asyncio.Task] = None


class PrinterConnectorService:
    """
    Manages connection to the currently enabled printer.
    
    Responsibilities:
    - Fetch enabled printer on startup
    - Create/maintain PrusaLinkClient connection
    - Handle printer change (disconnect old, connect new)
    - Run job watcher for the active printer
    """

    def __init__(
        self,
        printer_repo: PrinterRepository,
        on_job_complete: Callable,
    ) -> None:
        self._printer_repo = printer_repo
        self._on_job_complete = on_job_complete
        self._connection: Optional[PrinterConnection] = None
        self._lock = asyncio.Lock()

    @property
    def current_printer(self) -> Optional[PrinterRecord]:
        return self._connection.printer if self._connection else None

    async def start(self) -> None:
        """Initialize connection to enabled printer on app startup."""
        _printer = self._printer_repo.get_by_status("ENABLED")
        if _printer:
            await self._connect(_printer)

    async def get_health_status(self) -> dict:
        """Check printer health by fetching status."""
        try:
            if not self._connection:
                return {"status": "error", "details": "No active connection"}
            _ = await self._connection.client.get_status()
        except Exception as e:
            return {"status": "error", "details": str(e)}
        
        return {"status": "ok"}

    async def stop(self) -> None:
        """Cleanup on app shutdown."""
        await self._disconnect()

    async def on_printer_enabled(self, printer: PrinterRecord) -> None:
        """Called when user enables a different printer."""
        async with self._lock:
            await self._disconnect()
            await self._connect(printer)

    async def on_printer_disabled(self) -> None:
        """Called when user disables the current printer."""
        async with self._lock:
            await self._disconnect()

    async def _connect(self, printer: PrinterRecord) -> None:
        """Establish connection and start job watcher."""
        _client = PrusaLinkClient(printer.ip or "", printer.token or "")
        await _client.__aenter__()
        
        _task: asyncio.Task = asyncio.create_task(
            self._run_job_watcher(_client)
        )
        
        self._connection = PrinterConnection(
            printer=printer,
            client=_client,
            watcher_task=_task,
        )

    async def _disconnect(self) -> None:
        """Stop watcher and cleanup connection."""
        if not self._connection:
            return
        
        if self._connection.watcher_task:
            self._connection.watcher_task.cancel()
            try:
                await self._connection.watcher_task
            except asyncio.CancelledError:
                pass
        
        if self._connection.client:
            await self._connection.client.__aexit__(None, None, None)
        
        self._connection = None

    async def _run_job_watcher(self, client: PrusaLinkClient) -> None:
        """Run job watcher loop, call handler on completion."""
        async for job in watch_jobs(client):
            await self._on_job_complete(job)



_printer_connector: Optional[PrinterConnectorService] = None


def get_printer_connector() -> PrinterConnectorService:
    global _printer_connector
    if _printer_connector is None:
        _printer_connector = PrinterConnectorService(
            printer_repo=SqlitePrinterRepository(),
            on_job_complete=filament_tracking.record_job_completion,
        )
    return _printer_connector
