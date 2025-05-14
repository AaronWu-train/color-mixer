# hw_agent/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict

# GET /
class StatusResponse(BaseModel):
    message: str = Field(..., description="message")

# GET /ping
class PingResponse(BaseModel):
    ok: bool = Field(..., description="服務是否可用")

class RGBResponse(BaseModel):
    rgb: List[int] = Field(..., min_items=3, max_items=3, ge=0, le=255, description="Raw sensor RGB")

class ResetResponse(BaseModel):
    ok: bool = Field(...)

class DoseRequest(BaseModel):
    recipe: Dict[str, float] = Field(..., description="每通道 mL 打料量")
    # TODO: 這裡需要決定參數，例如時間、容量等

class DoseResponse(BaseModel):
    job_id: str = Field(...)

class StatusResponse(BaseModel):
    busy: bool = Field(..., description="泵浦是否運行中")
    pct: float = Field(..., ge=0, le=100, description="完成百分比")
