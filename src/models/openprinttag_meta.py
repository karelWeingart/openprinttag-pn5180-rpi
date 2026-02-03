# Meta section model
from typing import Optional

from pydantic import Field, BaseModel, ConfigDict, model_validator


class OpenPrintTagMeta(BaseModel):
    """
    OpenPrintTag meta section.
    """

    model_config = ConfigDict()

    @model_validator(mode="before")
    @classmethod
    def __convert_int_keys_to_str(cls, data):
        """Convert integer keys to string keys for alias matching."""
        if isinstance(data, dict):
            return {str(k) if isinstance(k, int) else k: v for k, v in data.items()}
        return data

    main_region_offset: Optional[int] = Field(None, alias="0")
    main_region_length: Optional[int] = Field(None, alias="1")
    aux_region_offset: Optional[int] = Field(None, alias="2")
    aux_region_length: Optional[int] = Field(None, alias="3")
