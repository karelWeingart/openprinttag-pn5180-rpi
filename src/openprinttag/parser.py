"""OpenPrintTag specs parser methods."""

from typing import Any, Optional
import cbor2
import io
from models.openprinttag_meta import OpenPrintTagMeta
from models.openprinttag_main import OpenPrintTagMain


def decode_openprinttag(
    payload: bytes,
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, object | None]:
    """
    OpenPrintTag payload = meta CBOR map + main CBOR map + optional aux CBOR map                                                                             .
    """
    try:
        dec = cbor2.CBORDecoder(io.BytesIO(payload))

        meta_dict = dec.decode()  # first CBOR object
        main = dec.decode()  # second CBOR object
        aux = dec.decode()  # optional

        return (
            OpenPrintTagMeta.model_validate(meta_dict),
            OpenPrintTagMain.model_validate(main),
            aux,
        )
    except Exception as e:
        raise ValueError(f"Failed to decode OpenPrintTag payload: {e}") from e


def extract_ndef_message_from_raw(raw: bytes) -> bytes:
    """
    Get the NDEF message bytes from raw tag memory.
    Supports TLV-wrapped and raw-at-offset-0 layouts.
    """
    # Try TLV first
    tlv_index = raw.find(b"\x03")
    if tlv_index != -1:
        length_byte = raw[tlv_index + 1]
        if length_byte != 0xFF:
            ndef_length = length_byte
            ndef_start = tlv_index + 2
        else:
            ndef_length = (raw[tlv_index + 2] << 8) | raw[tlv_index + 3]
            ndef_start = tlv_index + 4
        return raw[ndef_start : ndef_start + ndef_length]

    # Fallback: assume NDEF starts at 0
    return raw


def iter_ndef_records(ndef: bytes):
    """
    Iterate over NDEF records in a single NDEF message.
    Yields (header, tnf, type, payload).
    """
    i = 0
    length = len(ndef)

    while i < length:
        header = ndef[i]
        mb = (header & 0x80) != 0
        me = (header & 0x40) != 0
        cf = (header & 0x20) != 0
        sr = (header & 0x10) != 0
        il = (header & 0x08) != 0
        tnf = header & 0x07

        # minimal sanity: TNF must be 0–6, but 3 bits guarantee that
        type_len = ndef[i + 1]

        if sr:
            payload_len = ndef[i + 2]
            offset = i + 3
        else:
            payload_len = int.from_bytes(ndef[i + 2 : i + 6], "big")
            offset = i + 6

        if il:
            id_len = ndef[offset]
            offset += 1 + id_len

        type_field = ndef[offset : offset + type_len]
        offset += type_len

        payload = ndef[offset : offset + payload_len]
        offset += payload_len

        yield {
            "header": header,
            "tnf": tnf,
            "mb": mb,
            "me": me,
            "cf": cf,
            "sr": sr,
            "il": il,
            "type": type_field,
            "payload": payload,
        }

        i = offset
        if me:
            break


def parse_openprinttag(
    raw: bytes,
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, object | None]:
    """
    Detect OpenPrintTag by MIME type and return (meta, main, aux).
    """
    ndef = extract_ndef_message_from_raw(raw)

    openprint_payload = None

    for rec in iter_ndef_records(ndef):
        # logging.error(rec)
        try:
            t = rec["type"].decode("ascii", errors="ignore")
        except UnicodeDecodeError:
            continue

        if t == "application/vnd.openprinttag":
            openprint_payload = rec["payload"]
            break

    if openprint_payload is None:
        # logging.error("No OpenPrintTag MIME record found")
        return None, None, None

    meta, main, aux = decode_openprinttag(openprint_payload)

    return meta, main, aux


def parse_system_info(system_info_bytes: bytes) -> Optional[dict[str, Any]]:
    """
    Parse the raw system information response from an ISO15693 tag.
    Args:
        system_info_bytes: Raw bytes from get_system_info()
    Returns:
        Dictionary with parsed system information, or None if parsing fails.
    """
    if not system_info_bytes or len(system_info_bytes) < 10:
        return None
    try:
        info: dict[str, Any] = {}
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
    except Exception:
        return None
