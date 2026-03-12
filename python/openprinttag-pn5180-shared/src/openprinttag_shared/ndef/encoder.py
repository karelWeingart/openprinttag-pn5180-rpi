"""Encoder for NDEF (NFC Data Exchange Format) messages.

Uses ndeflib for NDEF record encoding, with custom TLV wrapping.
"""

import ndef  # type: ignore[import-untyped]


def build_ndef_message(records: list[ndef.Record]) -> bytes:
    """
    Build an NDEF message from a list of ndef.Record objects.
    Returns raw NDEF bytes (without TLV wrapper).
    """
    return b"".join(ndef.message_encoder(records))


def build_mime_record(mime_type: str, data: bytes) -> ndef.Record:
    """
    Create an NDEF record with MIME type (TNF=0x02).
    """
    return ndef.Record(mime_type, data=data)


def wrap_ndef_in_tlv(ndef_message: bytes) -> bytes:
    """
    Wrap NDEF message bytes in TLV format for NFC tag memory.

    TLV structure:
    - Type: 0x03 (NDEF Message)
    - Length: 1 byte if < 255, else 0xFF + 2 bytes
    - Value: NDEF message bytes
    - Terminator: 0xFE
    """
    length = len(ndef_message)

    if length < 0xFF:
        tlv = bytes([0x03, length]) + ndef_message
    else:
        # 3-byte length format
        tlv = bytes([0x03, 0xFF, (length >> 8) & 0xFF, length & 0xFF]) + ndef_message

    # Add terminator TLV
    return tlv + b"\xfe"
