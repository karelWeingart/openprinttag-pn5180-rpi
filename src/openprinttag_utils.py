"""
Simplified wrapper around vendored OpenPrintTag utilities.

This module provides easy-to-use functions for reading
OpenPrintTag NDEF records from NFC tags and converting
them to type-safe Pydantic models.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from openprinttag_vendored.record import Record
from models.fields import Schema

# Default config path
DEFAULT_CONFIG = Path(__file__).parent / "openprinttag_vendored" / "data" / "config_nfcv.yaml"


def load_config(_config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load OpenPrintTag configuration from YAML file."""
    if _config_path is None:
        _config_path = DEFAULT_CONFIG
    
    with open(_config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_ndef_record(_raw_data: bytes, _config_path: Optional[Path] = None) -> Record:
    """
    Parse raw NDEF data from an OpenPrintTag.
    
    Args:
        _raw_data: Raw bytes read from the NFC tag
        _config_path: Optional path to config YAML file
        
    Returns:
        Record object containing parsed tag data
    """
    _config = load_config(_config_path)
    _config_file = str(_config_path) if _config_path else str(DEFAULT_CONFIG)
    
    _record = Record(_config_file, memoryview(_raw_data))
    return _record


def read_tag_info(_record: Record) -> Schema:
    """
    Extract human-readable information from a parsed OpenPrintTag record
    and return as type-safe Pydantic models.
    
    Args:
        _record: Parsed Record object
        
    Returns:
        Schema object containing Main, Aux, and Meta region data as Pydantic models
    """
    _data = {}
    
    if _record.main_region:
        _data["main"] = _record.main_region.read()
    
    if _record.aux_region:
        _data["aux"] = _record.aux_region.read()
    
    if _record.meta_region:
        _data["meta"] = _record.meta_region.read()
    
    return Schema(**_data)
