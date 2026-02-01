from common.api import register_event
from common.enum import TagReadEvent
from models.event_dto import EventDto
from pn5180.sensor import ISO15693Sensor
import time
from pn5180.definitions import CMD_SEND_DATA
from typing import Optional, Any, Dict


class PreCommandError(Exception):
    """Custom exception for pre-command setup errors."""

    pass


class PostCommandError(Exception):
    """Custom exception for post-command cleanup errors."""

    pass


class CommandError(Exception):
    """Custom exception for get-system-info command."""

    ...


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
        Overrides base method to ensure proper setup.
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

    def __get_response_data(self) -> bytearray:
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

    def parse_system_info(self, system_info_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse the raw system information response from an ISO15693 tag.

        Args:
            system_info_bytes: Raw bytes from get_system_info()

        Returns:
            Dictionary with parsed system information, or None if parsing fails.
        """
        if not system_info_bytes or len(system_info_bytes) < 10:
            self._log(
                f"System info too short: {len(system_info_bytes) if system_info_bytes else 0} bytes"
            )
            return None

        try:
            info = {}
            idx = 0

            # Byte 0: Response flags
            info["response_flags"] = system_info_bytes[idx]
            idx += 1

            # Byte 1: Information flags (tells us what follows)
            info_flags = system_info_bytes[idx]
            info["info_flags"] = info_flags
            idx += 1

            # Byte 2-9: UID (8 bytes, reversed)
            uid_bytes = system_info_bytes[idx : idx + 8]
            info["uid"] = ":".join(f"{b:02x}" for b in uid_bytes)
            idx += 8

            # Optional fields based on info_flags bits
            # Bit 0: DSFID is supported and present
            if info_flags & 0x01 and idx < len(system_info_bytes):
                info["dsfid"] = system_info_bytes[idx]
                idx += 1

            # Bit 1: AFI is supported and present
            if info_flags & 0x02 and idx < len(system_info_bytes):
                info["afi"] = system_info_bytes[idx]
                idx += 1

            # Bit 2: Memory size info present (2 bytes)
            if info_flags & 0x04 and idx + 1 < len(system_info_bytes):
                num_blocks = system_info_bytes[idx] + 1  # Actual number is value + 1
                block_size = system_info_bytes[idx + 1] & 0x1F  # Lower 5 bits
                block_size_bytes = block_size + 1  # Actual size is value + 1
                info["num_blocks"] = num_blocks
                info["block_size"] = block_size_bytes
                info["total_memory_bytes"] = num_blocks * block_size_bytes
                idx += 2

            # Bit 3: IC reference present
            if info_flags & 0x08 and idx < len(system_info_bytes):
                info["ic_reference"] = system_info_bytes[idx]
                idx += 1

            return info

        except Exception as e:
            self._log(f"Error parsing system info: {e}")
            return None

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
        _raw = b""
        try:
            self.__pre_command()
            for _block in range(blocks):
                _block_start = time.time()

                _data: bytearray = None
                # while _data is None:
                _data = self.read_single_block(_block, pre_command=False)

                #    if time.time() - _block_start > self._BLOCK_READ_TIMEOUT:
                #        break

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
