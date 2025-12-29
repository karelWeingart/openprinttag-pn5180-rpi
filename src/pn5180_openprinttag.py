from pypn5180.iso_iec_15693 import iso_iec_15693
from openprinttag_utils import parse_ndef_record, read_tag_info
from models.fields import Schema

class Pn5180OpenPrintTag(iso_iec_15693):
    """Class for interacting with Open Print Tags using the PN5180 NFC controller."""

    def inventoryCmd(self):
        """
        Perform ISO15693 Inventory command (single slot).
        Returns a list of UIDs (each UID is bytes).
        """
        _cmd_flags = 0x26

        _mask_len = 0x00
        _frame = []

        _frame.insert(0, _cmd_flags)
        _frame.insert(1, self.CMD_CODE["INVENTORY"])
        _frame.insert(2, _mask_len)

        _flags, _data = self.pn5180.transactionIsoIec15693(_frame)
        _data, _error = self.getError(_flags, _data)
        return [_data]

    def read_ndef_data(self, uid: bytes = None, start_block: int = 0, num_blocks: int = 32) -> bytes:
        """
        Read NDEF data from the tag.
        
        Args:
            uid: UID of the tag to read from (optional, uses addressed mode if provided)
            start_block: Starting block number (default: 0)
            num_blocks: Number of blocks to read (default: 32, reads 128 bytes)
            
        Returns:
            Raw NDEF data as bytes
        """
        _uid_list = list(uid) if uid else []
        _flags, _data = self.readMultipleBlocksCmd(start_block, num_blocks, _uid_list)
        _data, _error = self.getError(_flags, _data)
        
        if _error:
            raise RuntimeError(f"Error reading NDEF data: {_error}")
        
        return bytes(_data)

    def read_openprinttag(self, uid: bytes = None) -> Schema:
        """
        Read and parse an OpenPrintTag from the NFC tag.
        
        Args:
            uid: UID of the tag to read from (optional)
            
        Returns:
            Schema object containing parsed tag data with Main, Aux, and Meta regions
        """
        # Read raw NDEF data from tag
        _raw_ndef = self.read_ndef_data(uid)
        
        # Parse NDEF record structure
        _record = parse_ndef_record(_raw_ndef)
        
        # Extract and validate data as Pydantic models
        return read_tag_info(_record)
