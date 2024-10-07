from pydantic import BaseModel

class Prediction(BaseModel):
    value: float
    n: int = None # relative horizon

class StreamPoint(BaseModel):
    substream_id: str
    value: float
    n: int = None      # relative time
