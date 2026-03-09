"""OpenPrintTag specs parser methods."""

from typing import Any, Optional

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
