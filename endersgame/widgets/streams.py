from pydantic import BaseModel

class Prediction(BaseModel):
    value: float
    ndx: int = None
    horizon: int = None

class StreamPoint(BaseModel):
    substream_id: str
    value: float
    ndx: int = None
