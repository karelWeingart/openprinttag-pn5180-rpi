# Meta section model
from typing import Optional

from pydantic import Field, BaseModel


class OpenPrintTagMeta(BaseModel):
    """
    OpenPrintTag meta section.
    Only main_length is mandatory when using sequential CBOR decoding.
    """
    version: Optional[int] = Field(None, alias="0")
    main_offset: Optional[int] = Field(None, alias="1")
    main_length: int = Field(..., alias="2")  # Mandatory
    aux_offset: Optional[int] = Field(None, alias="3")
    aux_length: Optional[int] = Field(None, alias="4")
    
    class Config:
        populate_by_name = True  # Allow both string keys and field names