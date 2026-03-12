"""Decoder for NDEF (NFC Data Exchange Format) messages.

Uses ndeflib for NDEF record decoding, with custom TLV extraction.
"""

import ndef  # type: ignore[import-not-found]
from typing import Iterator


def extract_ndef_message_from_raw(raw: bytes) -> bytes:
    """
    Get the NDEF message bytes from raw tag memory.
    Supports TLV-wrapped and raw-at-offset-0 layouts.

    Note: ndeflib doesn't handle TLV extraction, so we keep this custom.
    """
    # Try TLV first (0x03 = NDEF Message TLV)
    tlv_index = raw.find(b"\x03")
    if tlv_index != -1:
        length_byte = raw[tlv_index + 1]
        if length_byte != 0xFF:
            ndef_length = length_byte
            ndef_start = tlv_index + 2
        else:
            # 3-byte length format
            ndef_length = (raw[tlv_index + 2] << 8) | raw[tlv_index + 3]
            ndef_start = tlv_index + 4
        return raw[ndef_start : ndef_start + ndef_length]

    # Fallback: assume NDEF starts at 0
    return raw


def iter_ndef_records(ndef_bytes: bytes) -> Iterator[ndef.Record]:
    """
    Iterate over NDEF records in a message.
    Yields ndef.Record objects from ndeflib.
    """
    yield from ndef.message_decoder(ndef_bytes)
