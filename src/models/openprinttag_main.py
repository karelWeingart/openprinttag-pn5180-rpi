""" main region of openprinttag data. 
now not all attributes are parsed.
"""
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, model_validator
from utils.conversion import closest_color


class OpenPrintTagMain(BaseModel):
    """
    OpenPrintTag main section containing filament/print information.
    Simplified model with human-readable properties.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def __convert_int_keys_to_str(cls, data):
        """Convert integer keys to string keys for alias matching.
        Needed for pydantic config...
        """
        if isinstance(data, dict):
            return {str(k) if isinstance(k, int) else k: v for k, v in data.items()}
        return data

    # Mapping for numeric material class -> human readable string
    _MATERIAL_CLASS_MAP = {
        0: "FFF",
        1: "SLA",
    }

    # Mapping for top 10 most-used material types (0-9), with "Other" fallback
    _MATERIAL_TYPE_MAP = {
        0: "PLA",
        1: "PETG",
        2: "TPU",
        3: "ABS",
        4: "ASA",
        5: "PC",
        6: "PCTG",
        7: "PP",
        8: "PA6",
        9: "PA12",
    }

    # Identification
    instance_uuid: Optional[bytes] = Field(None, alias="0")
    package_uuid: Optional[bytes] = Field(None, alias="1")
    material_uuid: Optional[bytes] = Field(None, alias="2")
    brand_uuid: Optional[bytes] = Field(None, alias="3")
    gtin: Optional[int] = Field(None, alias="4")
    brand_specific_instance_id: Optional[str] = Field(None, alias="5")

    # Material information
    material_class_raw: int = Field(..., alias="8")
    material_name: Optional[str] = Field(None, alias="10")
    manufacturer: Optional[str] = Field(None, alias="11")
    material_abbreviation: Optional[str] = Field(None, alias="52")
    material_type_raw: Optional[int] = Field(None, alias="9")

    manufactured_date_raw: Optional[int] = Field(None, alias="14")

    # Dimensions & measurements
    nominal_netto_full_weight: Optional[int] = Field(None, alias="16")
    actual_netto_full_weight: Optional[int] = Field(None, alias="17")
    empty_container_weight: Optional[int] = Field(None, alias="18")

    # Color (3 or 4 bytes RGB(A)) - keep raw bytes internal
    primary_color_raw: Optional[bytes] = Field(None, alias="19")

    # Temperature settings (in Celsius)
    min_print_temperature: Optional[int] = Field(None, alias="34")
    max_print_temperature: Optional[int] = Field(None, alias="35")
    preheat_temperature: Optional[int] = Field(None, alias="36")
    min_bed_temperature: Optional[int] = Field(
        None, alias="37"
    )  # Minimum nozzle temperature
    max_bed_temperature: Optional[int] = Field(
        None, alias="38"
    )  # Maximum nozzle temperature

    @property
    def primary_color_hex(self) -> Optional[str]:
        """Get color as hex string (e.g., '#RRGGBB'). Uses the first three bytes of RGB(A)."""
        raw = getattr(self, "primary_color_raw", None)
        if not raw:
            return None
        if not isinstance(raw, (bytes, bytearray)):
            return None
        if len(raw) < 3:
            return None
        # take first three bytes (ignore alpha if present)
        r, g, b = raw[0], raw[1], raw[2]
        return f"#{r:02X}{g:02X}{b:02X}"

    @property
    def material_class(self) -> str:
        """Return human-readable material class (e.g. 'FFF', 'SLA')"""
        return self._MATERIAL_CLASS_MAP.get(
            self.material_class_raw, f"Unknown({self.material_class_raw})"
        )

    @property
    def material_type(self) -> Optional[str]:
        """Return human-readable material type (e.g. 'PLA', 'PETG', ..., 'Other').

        Maps the numeric material_type_raw to the top 10 most-used materials,
        with fallback to 'Other' for unknown types.
        """
        if self.material_type_raw is None:
            return None
        return self._MATERIAL_TYPE_MAP.get(self.material_type_raw, "Other")

    def model_dump(self, *args, **kwargs):
        """Customize serialization: hide raw numeric fields and expose mapped string values."""
        data = super().model_dump(*args, **kwargs)

        # Add computed/mapped values
        data["material_class"] = self.material_class
        data["material_type"] = self.material_type
        data["primary_color"] = self.primary_color_hex
        data["manufactured_date"] = self.manufactured_date
        
        return data

    @property
    def manufactured_date(self) -> Optional[str]:
        """Return manufactured date as ISO8601 string (UTC) or None."""
        if self.manufactured_date_raw is None:
            return None
        try:
            return datetime.fromtimestamp(
                int(self.manufactured_date_raw), tz=timezone.utc
            ).isoformat()
        except Exception:
            return f"InvalidTimestamp({self.manufactured_date_raw})"

    @property
    def uuid_hex(self) -> Optional[str]:
        """Get UUID as hex string"""
        if self.instance_uuid and isinstance(self.instance_uuid, bytes):
            return self.instance_uuid.hex()
        return None
    
    def get_human_readable_color(self) -> Optional[str]:
        """Get human-readable color name"""
        hex_color = self.primary_color_hex
        if hex_color is None:
            return None
        return closest_color(hex_color)

    def __repr__(self) -> str:
        """String representation with manufacturer, filament name, and type"""
        parts = []
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.material_name:
            parts.append(self.material_name)
        # Use the human-readable material class string
        if getattr(self, "material_class", None) is not None:
            parts.append(f"Type: {self.material_class}")
        return " - ".join(parts) if parts else "Unknown filament"
