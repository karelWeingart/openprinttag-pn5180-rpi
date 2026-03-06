from pydantic import BaseModel


class EventMessage(BaseModel):
    """Model for the MQTT event message payload.
    This one is used for generating messages sent by the pn5180 reader
    that are consumed by the web API.
    """

    event_type: str
    error: str | None = None
    tag_uid: str | None = None
    material_type: str | None = None
    manufacturer: str | None = None
    name: str | None = None
    color: str | None = None
