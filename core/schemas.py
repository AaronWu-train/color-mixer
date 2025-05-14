# core/schemas.py
from pydantic import BaseModel, Field, conlist
from typing import Literal, List, Dict
from uuid import UUID

# GET /
class StatusResponse(BaseModel):
    message: str = Field(..., description="message")

# GET /ping
class PingResponse(BaseModel):
    ok: bool = Field(..., description="服務是否可用")

# POST /mix
class MixRequest(BaseModel):
    rgb: List[int] = Field(..., min_items=3, max_items=3, ge=0, le=255, description="目標 RGB")

class MixResponse(BaseModel):
    session: UUID = Field(..., description="混色作業識別碼")

# POST /reset
class ResetResponse(BaseModel):
    ok: bool = Field(..., description="是否已成功重置硬體")

# Websocket /ws/color
class WSColorResponse(BaseModel):
    rgb: List[int] = Field(..., min_items=3, max_items=3, ge=0, le=255, description="感測到的 RGB")

# Websocket /ws/mix
# [TODO] 根據我們需求修改這些狀態的內容

class WSMixStarted(BaseModel):
    state: Literal["started"] = Field(
        "started", description="狀態：已啟動混色流程"
    )
    recipe: Dict[str, float] = Field(
        ...,
        description="各通道打料量 (mL)， key 為 channel ID"
    )


class WSMixProgress(BaseModel):
    state: Literal["progress"] = Field(
        "progress", description="狀態：混色中"
    )
    pct: float = Field(
        ..., ge=0, le=100, description="完成百分比"
    )


class WSMixFinished(BaseModel):
    state: Literal["finished"] = Field(
        "finished", description="狀態：混色完成"
    )
    deltaE: float = Field(
        ..., ge=0, description="最終色差 ΔE"
    )
    final_rgb: List[int] = Field(
        ..., min_items=3, max_items=3, ge=0, le=255,
        description="混色後最終 RGB"
    )


class WSMixError(BaseModel):
    state: Literal["error"] = Field(
        "error", description="狀態：錯誤"
    )
    msg: str = Field(
        ..., description="錯誤訊息"
    )