from common.api import register_event
from common.enum import TagReadEvent
from models.event_dto import EventDto
from pn5180.sensor import ISO15693Sensor
import time
from pn5180.definitions import CMD_SEND_DATA
from typing import Optional, Any, Dict


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
    _BLOCK_READ_EVENT_STEP = 10  # Trigger BLOCK_UPLOADED event every N blocks

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

    def __command(self, frame: bytearray, pre_command: bool = True) -> bytearray:
        """ sends PN5180 command and waits for data. """
        if pre_command:
            self.__pre_command()

        try:
            self._write(frame)

            time.sleep(self._READ_WAIT_TIME)

            _response: bytearray = self.__get_response_data()

            return bytes(_response)
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
        _response: bytearray = self._read(_response_length)

        _response_flags = _response[0]
        if _response_flags & 0x01:
            self._log(f"Error flag set in response (flags: 0x{_response_flags:02x})")
            raise RuntimeError("Tag returned error response")
        return _response

    def get_system_info(self) -> Optional[bytes]:
        """
        Get system information from an ISO15693 tag.

        Returns:
            Raw response bytes from Get System Information command, or None if error.
        """
        _flags = 0x02
        _command = 0x2B
        _frame = [CMD_SEND_DATA, 0x00, _flags, _command]
        return self.__command(_frame)

    def read_single_block(self, block: int, pre_command: bool = True) -> bytes:
        """
        Read a single ISO15693 block.
        Returns raw block data (bytes) or None.
        """
        frame = [CMD_SEND_DATA, 0x00, 0x02, 0x20, block]
        _data = self.__command(frame, pre_command=pre_command)
        if _data:
            return bytes(_data[1:])
        return None

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

                _data: bytearray = None
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
