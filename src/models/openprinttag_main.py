from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class OpenPrintTagMain(BaseModel):
    """
    OpenPrintTag main section containing filament/print information.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    # Identification
    uuid: Optional[bytes] = Field(None, alias="0")  # 16-byte UUID
    serial_number: Optional[str] = Field(None, alias="5")
    
    # Material information
    material_type: Optional[int] = Field(None, alias="8")  # Material type code
    material_name: Optional[str] = Field(None, alias="10")  # e.g., "Woodfill Pastel Brown"
    manufacturer: Optional[str] = Field(None, alias="11")  # e.g., "Prusament"
    
    # Timestamps
    production_timestamp: Optional[int] = Field(None, alias="14")  # Unix timestamp
    
    # Dimensions & measurements
    total_length: Optional[int] = Field(None, alias="17")  # Total filament length in mm
    remaining_length: Optional[int] = Field(None, alias="54")  # Remaining length in mm
    weight: Optional[int] = Field(None, alias="18")  # Weight in grams
    
    # Color (3 bytes RGB)
    color_rgb: Optional[bytes] = Field(None, alias="19")  # RGB color bytes
    
    # Physical properties
    diameter: Optional[float] = Field(None, alias="30")  # Filament diameter in mm (e.g., 1.75)
    
    # Temperature settings (in Celsius)
    nozzle_temp: Optional[int] = Field(None, alias="34")  # Recommended nozzle temperature
    bed_temp: Optional[int] = Field(None, alias="35")  # Recommended bed temperature
    min_nozzle_temp: Optional[int] = Field(None, alias="37")  # Minimum nozzle temperature
    max_nozzle_temp: Optional[int] = Field(None, alias="38")  # Maximum nozzle temperature
    
    @property
    def color_hex(self) -> Optional[str]:
        """Get color as hex string (e.g., '#dfbf9f')"""
        if self.color_rgb and isinstance(self.color_rgb, bytes) and len(self.color_rgb) == 3:
            return f"#{self.color_rgb.hex()}"
        return None
    
    @property
    def uuid_hex(self) -> Optional[str]:
        """Get UUID as hex string"""
        if self.uuid and isinstance(self.uuid, bytes):
            return self.uuid.hex()
        return None
