from datetime import datetime

from pydantic import BaseModel


class Prediction(BaseModel):
    value: float
    # TODO: Oneof?
    t: datetime = None # absolute time
    n: int = None # relative horizon

class StreamPoint(BaseModel):
    substream_id: str
    value: float
    t: datetime = None # absolute time
    n: int = None      # relative time

class StreamBatch(BaseModel):
    points: list[StreamPoint] = []
