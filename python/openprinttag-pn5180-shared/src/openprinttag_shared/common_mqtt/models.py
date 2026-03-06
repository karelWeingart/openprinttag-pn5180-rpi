from pydantic import BaseModel, Field

class EventMessage(BaseModel):
    """ Model for the MQTT event message payload. 
    This one is used for generating messages sent by the pn5180 reader 
    that are consumed by the web API.
    """
    event_type: str = Field(..., description="Type of the event")
    error: str | None = Field(None, description="Error message. Empty if no error.")
    tag_uid: str | None = Field(None, description="UID of the tag.")
    material_type: str | None = Field(None, description="Material type of the fillament.")
    manufacturer: str | None = Field(None, description="Manufacturer of the filament.")
    name: str | None = Field(None, description="Name of the filament.")
    color: str | None = Field(None, description="Color of the filament.")
