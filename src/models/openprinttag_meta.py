# Meta section model
from typing import Optional

from pydantic import Field, BaseModel


class OpenPrintTagMeta(BaseModel):
    """
    OpenPrintTag meta section.
    """

    main_region_offset: Optional[int] = Field(None, alias="0")
    main_region_length: Optional[int] = Field(None, alias="1")
    aux_region_offset: Optional[int] = Field(None, alias="2")
    aux_region_length: Optional[int] = Field(None, alias="3")

    class Config:
        populate_by_name = True  # Allow both string keys and field names
