"""Parser for bgcode file metadata."""

import re
from typing import Optional

import requests
from pydantic import BaseModel


class GcodeMetadata(BaseModel):
    """Metadata extracted from (b)gcode file header."""

    filament_type: Optional[str] = None
    filament_used_mm: Optional[float] = None
    filament_used_g: Optional[float] = None
    filament_used_cm3: Optional[float] = None
    estimated_print_time: Optional[int] = None  # seconds


def parse_gcode_header(data: bytes) -> GcodeMetadata | None:
    """Parse metadata from (b)gcode file header.

    Args:
        data: First ~4KB of (b)gcode file (header contains metadata as text)

    Returns:
        GcodeMetadata with extracted values
    """
    if not data:
        return None

    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = str(data)

    metadata = GcodeMetadata()

    # Pattern matchers for key=value pairs
    patterns = {
        "filament_type": (r"filament_type=(\w+)", str),
        "filament_used_mm": (r"filament used \[mm\]=([0-9.]+)", float),
        "filament_used_g": (r"filament used \[g\]=([0-9.]+)", float),
        "filament_used_cm3": (r"filament used \[cm3\]=([0-9.]+)", float),
        "estimated_print_time": (r"estimated printing time.*?=\s*(\d+)", int),
    }

    for field, (pattern, converter) in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                setattr(metadata, field, converter(match.group(1)))
            except (ValueError, TypeError):
                pass

    return metadata

def calculate_filament_used(
    metadata: GcodeMetadata,
    progress_percent: float,
) -> dict[str, Optional[float]]:
    """Calculate actual filament used based on progress.

    Args:
        metadata: Parsed bgcode metadata
        progress_percent: Current print progress (0-100)

    Returns:
        Dict with used_mm, used_g, used_cm3 based on progress
    """
    factor = progress_percent / 100.0

    return {
        "used_mm": metadata.filament_used_mm * factor
        if metadata.filament_used_mm
        else None,
        "used_g": metadata.filament_used_g * factor
        if metadata.filament_used_g
        else None,
        "used_cm3": metadata.filament_used_cm3 * factor
        if metadata.filament_used_cm3
        else None,
        "total_g": metadata.filament_used_g,
        "progress_percent": progress_percent,
    }
