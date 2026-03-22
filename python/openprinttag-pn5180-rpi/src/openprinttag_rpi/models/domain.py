from pydantic import BaseModel

class FilamentUsageMessage(BaseModel):

  job_id: int
  tag_uid: str
  filament_usage: float
  timestamp: str
  status: str