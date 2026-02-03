import cbor2
import io
from models.openprinttag_meta import OpenPrintTagMeta
from models.openprinttag_main import OpenPrintTagMain


def decode_openprinttag(
    payload: bytes,
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, dict | None]:
    """
    OpenPrintTag payload = meta CBOR map + main CBOR map + optional aux CBOR map                                                                             .
    """
    try:
        dec = cbor2.CBORDecoder(io.BytesIO(payload))

        meta_dict = dec.decode()  # first CBOR object
        main = dec.decode()  # second CBOR object
        aux = dec.decode()  # optional

        return OpenPrintTagMeta.model_validate(meta_dict), OpenPrintTagMain.model_validate(main), aux
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
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, dict | None]:
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
