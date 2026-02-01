from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class OpenPrintTagMain(BaseModel):
    """
    OpenPrintTag main section containing filament/print information.
    Simplified model with human-readable properties.
    """

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

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
        # Remove the raw numeric fields
        data.pop("material_class_raw", None)
        data.pop("material_type_raw", None)
        # Remove raw manufactured timestamp and expose formatted date
        raw_ts = data.pop("manufactured_date_raw", None)
        try:
            if raw_ts is not None:
                data["manufactured_date"] = datetime.fromtimestamp(
                    int(raw_ts), tz=timezone.utc
                ).isoformat()
            else:
                data["manufactured_date"] = None
        except Exception:
            data["manufactured_date"] = f"InvalidTimestamp({raw_ts})"
        # Remove raw primary color bytes and expose hex string
        raw_color = data.pop("primary_color_raw", None)
        try:
            if raw_color is not None:
                # convert raw bytes to #RRGGBB using first three bytes
                if isinstance(raw_color, (bytes, bytearray)) and len(raw_color) >= 3:
                    r, g, b = raw_color[0], raw_color[1], raw_color[2]
                    data["primary_color"] = f"#{r:02X}{g:02X}{b:02X}"
                else:
                    data["primary_color"] = None
            else:
                data["primary_color"] = None
        except Exception:
            data["primary_color"] = f"InvalidColor({raw_color})"
        # Expose the mapped string values
        data["material_class"] = self.material_class
        data["material_type"] = self.material_type
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
