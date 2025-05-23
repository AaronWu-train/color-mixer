"""Pydantic schemas for the Color Mixer core API."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, RootModel, conint, conlist


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class State(str, Enum):
    """Operational state of the mixer core."""

    accepted = "accepted"  # 已接收請求，待處理
    idle = "idle"  # 閒置
    running = "running"  # 混色中
    finished = "finished"  # 混色完成，完成後應該持續此狀態 3 秒
    error = "error"  # 發生錯誤


# --------------------------------------------------------------------------- #
# Primitive value objects
# --------------------------------------------------------------------------- #
class RGBColorArray(
    RootModel[
        conlist(
            conint(ge=0, le=255),  # 每個元素 0–255
            min_length=3,
            max_length=3,  # 僅接受正好 3 筆 (R, G, B)
        )
    ]
):
    """RGB color after scaling (0 – 255)."""


# --------------------------------------------------------------------------- #
# Request & response models
# --------------------------------------------------------------------------- #
class MessageResponse(BaseModel):
    """Standard OK/NG envelope without additional payload."""

    ok: bool = Field(..., description="Indicates whether the call succeeded.")
    message: str = Field(..., description="Human‑readable message.")


class StatusResponse(BaseModel):
    """Current runtime status of the mixer core."""

    state: State
    message: Optional[str] = Field(None, description="Detail message.")


class ErrorResponse(BaseModel):
    """Generic error wrapper."""

    error: str = Field(..., description="Error message.")


class MixRequest(BaseModel):
    """Request to start a color mixing session."""

    target: RGBColorArray = Field(
        ..., description="Target RGB color to be mixed (scaled 0 – 255)."
    )
    message: Optional[str] = Field(
        None,
        description="Optional message to pass to the algorithm (for logging, etc.).",
    )
