"""Parser for OpenPrintTag payloads."""

import cbor2
import io
from openprinttag_shared.models.openprinttag_meta import OpenPrintTagMeta
from openprinttag_shared.models.openprinttag_main import OpenPrintTagMain
from openprinttag_shared.ndef.decoder import (
    extract_ndef_message_from_raw,
    iter_ndef_records,
)

OPENPRINTTAG_MIME_TYPE = "application/vnd.openprinttag"


def _decode_openprinttag(
    payload: bytes,
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, object | None]:
    """
    OpenPrintTag payload = meta CBOR map + main CBOR map + optional aux CBOR map.
    """
    try:
        _dec = cbor2.CBORDecoder(io.BytesIO(payload))

        _meta_dict = _dec.decode()  # first CBOR object
        _main = _dec.decode()  # second CBOR object
        _aux = _dec.decode()  # optional

        return (
            OpenPrintTagMeta.model_validate(_meta_dict),
            OpenPrintTagMain.model_validate(_main),
            _aux,
        )
    except Exception as e:
        raise ValueError(f"Failed to decode OpenPrintTag payload: {e}") from e


def parse_openprinttag(
    raw: bytes,
) -> tuple[OpenPrintTagMeta | None, OpenPrintTagMain | None, object | None]:
    """
    Detect OpenPrintTag by MIME type and return (meta, main, aux).
    """
    ndef_bytes = extract_ndef_message_from_raw(raw)

    openprint_payload = None

    for record in iter_ndef_records(ndef_bytes):
        if record.type == OPENPRINTTAG_MIME_TYPE:
            openprint_payload = record.data
            break

    if openprint_payload is None:
        return None, None, None

    _meta, _main, _aux = _decode_openprinttag(openprint_payload)

    return _meta, _main, _aux
