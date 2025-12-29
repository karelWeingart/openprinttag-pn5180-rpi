"""
Vendored utilities from OpenPrintTag repository.
Source: https://github.com/prusa3d/OpenPrintTag

Copyright 2025 PRUSA RESEARCH A.S.
Licensed under MIT License - see LICENSE file in this directory.

This package contains the core utilities for encoding/decoding OpenPrintTag data
without requiring the full OpenPrintTag package installation.
"""

from .fields import Fields, EncodeConfig, Field
from .record import Record, Region

__all__ = ["Fields", "EncodeConfig", "Field", "Record", "Region"]
