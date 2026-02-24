from common.api import register_event
from common.enum import TagReadEvent
from models.event_dto import EventDto
from pn5180.sensor import ISO15693Sensor
import time
from pn5180.definitions import CMD_SEND_DATA


class PreCommandError(Exception):
    """Custom exception for pre-command setup errors."""

class PostCommandError(Exception):
    """Custom exception for post-command cleanup errors."""

class CommandError(Exception):
    """ Custom exception for any command."""

class ExtendedISO15693Sensor(ISO15693Sensor):
    """
    Extension of ISO15693Sensor adding block-level read support.
    Works in non-addressed mode (one tag in field).
    """

    _READ_WAIT_TIME = 0.01  # seconds
    _BLOCK_READ_TIMEOUT = 0.1  # seconds
    _BLOCK_WRITE_TIMEOUT = 0.15  # seconds (writes take longer than reads)
    _BLOCK_READ_EVENT_STEP = 10  # Trigger BLOCK_UPLOADED event every N blocks
    _BLOCK_WRITE_EVENT_STEP = 10  # Trigger BLOCK_WRITTEN event every N blocks
    _DEFAULT_BLOCK_SIZE = 4  # bytes per block (ISO15693 typical)

    def __pre_command(self) -> None:
        """
        Prepares the PN5180 for sending a command.
        """
        try:
            self._load_protocol()
            self._turn_on_rf_field()
            self._clear_interrupt_register()
            self._set_idle_state()
            self._activate_transceive_routine()
        except Exception as e:
            raise PreCommandError(f"Error in pre-command setup: {e}") from e

    def __post_command(self) -> None:
        """
        Cleans up the PN5180 after sending a command.
        """
        try:
            self._set_send_eof()
            self._set_idle_state()
            self._activate_transceive_routine()
            self._clear_interrupt_register()
            self._send_eof()
            self._turn_off_rf_field()
        except Exception as e:
            raise PostCommandError(f"Error in post-command setup: {e}") from e

    def __command(self, frame: bytearray, pre_command: bool = True) -> bytes:
        """ sends PN5180 command and waits for data. """
        if pre_command:
            self.__pre_command()

        try:
            self._write(frame)  # type: ignore[arg-type]

            time.sleep(self._READ_WAIT_TIME)

            _response: bytearray | None = self.__get_response_data()

            return bytes(_response) if _response else b""
        except Exception as e:
            raise CommandError(f"Error getting data for a command: {e}") from e
        finally:
            if pre_command:
                self.__post_command()

    def __get_response_data(self) -> bytearray | None:
        """
        Helper to read response data from the PN5180 after sending a command.
        Returns list of response bytes or None.
        """
        _response_length: int = self._get_card_response_bytes()

        if _response_length == 0:
            self._log("No response received")
            return None

        self._read_data_cmd()
        _response: bytearray = self._read(_response_length)  # type: ignore[assignment]

        _response_flags = _response[0]
        if _response_flags & 0x01:
            self._log(f"Error flag set in response (flags: 0x{_response_flags:02x})")
            raise RuntimeError("Tag returned error response")
        return _response

    def get_system_info(self) -> bytes:
        """
        Get system information from an ISO15693 tag.

        Returns:
            Raw response bytes from Get System Information command, or None if error.
        """
        _flags = 0x02
        _command = 0x2B
        _frame: bytearray = bytearray([CMD_SEND_DATA, 0x00, _flags, _command])
        return self.__command(_frame)

    def read_single_block(self, block: int, pre_command: bool = True) -> bytes | None:
        """
        Read a single ISO15693 block.
        Returns raw block data (bytes) or None.
        """
        frame = bytearray([CMD_SEND_DATA, 0x00, 0x02, 0x20, block])
        _data = self.__command(frame, pre_command=pre_command)
        if _data:
            return bytes(_data[1:])
        return None

    def write_single_block(self, block: int, data: bytes, pre_command: bool = True) -> bool:
        """
        Write a single ISO15693 block.
        Args:
            block: Block number to write.
            data: Block data bytes (must match tag's block size, typically 4 bytes).
            pre_command: Whether to run pre/post command setup.
        Returns:
            True if write succeeded, False otherwise.
        """
        # ISO15693 Write Single Block: flags=0x02 (non-addressed), command=0x21
        frame = bytearray([CMD_SEND_DATA, 0x00, 0x02, 0x21, block] + list(data))
        response = self.__command(frame, pre_command=pre_command)
        return response is not None

    def write_multi_blocks(self, data: bytes, block_size: int = _DEFAULT_BLOCK_SIZE) -> bool:
        """ Writes data block by block to the tag.
        Data is split into chunks of block_size bytes.
        Simple timeout is implemented - if a block is not written within
        _BLOCK_WRITE_TIMEOUT, an exception is thrown.
        Events for callbacks are registered:
        - BLOCK_WRITTEN: for every 10th block written.
        - ERROR: for any failure during writing.

        Args:
            data: Raw bytes to write (will be padded to block_size alignment).
            block_size: Tag block size in bytes (default 4).
        Returns:
            True if all blocks written successfully, False otherwise.
        """
        # Pad data to block_size alignment
        if len(data) % block_size != 0:
            data = data + b'\x00' * (block_size - len(data) % block_size)

        num_blocks = len(data) // block_size

        try:
            self.__pre_command()
            for _block in range(num_blocks):
                _block_start = time.time()
                _chunk = data[_block * block_size : (_block + 1) * block_size]

                _written = False
                while not _written:
                    _written = self.write_single_block(_block, _chunk, pre_command=False)
                    if time.time() - _block_start > self._BLOCK_WRITE_TIMEOUT:
                        break

                if not _written:
                    raise CommandError(f"Timeout writing block {_block}")

                if (_block + 1) % self._BLOCK_WRITE_EVENT_STEP == 0:
                    register_event(
                        EventDto(
                            event_type=TagReadEvent.BLOCK_WRITTEN,
                            data={"block": _block, "blocks": num_blocks},
                        )
                    )
            return True
        except (CommandError, PreCommandError) as e:
            register_event(
                EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)})
            )
            return False
        finally:
            self.__post_command()

    def read_multi_blocks(self, blocks: int) -> bytes:
        """ Reads block by block iterating each till blocks reached.
        Simple timeout is implemented - if block is not loaded within
        _BLOCK_READ_TIMEOUT exception is thrown and tag must be re-read.
        events for callbacks are registered:
        - BLOCK_UPLOADED: for every 10th block read.
        - ERROR: for any blocking failure during the reading.
        """
        _raw = b""
        try:
            self.__pre_command()
            for _block in range(blocks):
                _block_start = time.time()

                _data: bytes | None = None
                while _data is None:
                    _data = self.read_single_block(_block, pre_command=False)
                    if time.time() - _block_start > self._BLOCK_READ_TIMEOUT:
                        break
                
                if _data is None:
                    raise CommandError(f"Timeout reading block {_block}")
                _raw += _data

                if (_block + 1) % self._BLOCK_READ_EVENT_STEP == 0:
                    register_event(
                        EventDto(
                            event_type=TagReadEvent.BLOCK_UPLOADED,
                            data={"block": _block, "blocks": blocks},
                        )
                    )
            return _raw
        except (CommandError, PreCommandError) as e:
            register_event(
                EventDto(event_type=TagReadEvent.ERROR, data={"error": str(e)})
            )
            return b""
        finally:
            self.__post_command()
