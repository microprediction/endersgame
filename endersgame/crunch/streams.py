from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Prediction(BaseModel):
    value: float
    t: Optional[datetime] = None # absolute time
    n: int = None # relative horizon

class StreamPoint(BaseModel):
    substream_id: Optional[str]
    value: float
    t: Optional[datetime] = None # absolute time
    n: int = None      # relative time

class StreamBatch(BaseModel):
    points: list[StreamPoint] = []
