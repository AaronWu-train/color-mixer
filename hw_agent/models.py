"""Pydantic schemas for the Color Mixer hardware‑agent API."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, conint, conlist


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class State(str, Enum):
    """Operational state of the hardware agent."""

    accepted = "accepted"  # 已接收請求，待處理
    idle = "idle"  # 閒置
    running = "running"  # 執行中
    finished = "finished"  # 完成上一指令，停留約 1~3 秒
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
    """sRGB color after scaling and correction (0 – 255)."""


# --------------------------------------------------------------------------- #
# Domain objects
# --------------------------------------------------------------------------- #
class PaintItem(BaseModel):
    """A single paint record in the palette."""

    id: int = Field(..., description="ID of the color, starting from 0.")
    name: str = Field(..., examples=["magenta"])
    rgb: RGBColorArray = Field(..., description="sRGB color (0 – 255)")


# --------------------------------------------------------------------------- #
# Request & response models
# --------------------------------------------------------------------------- #
class MessageResponse(BaseModel):
    """Standard OK/NG envelope without additional payload."""

    ok: bool = Field(..., description="Indicates whether the call succeeded.")
    message: str = Field(..., description="Human‑readable message.")


class StatusResponse(BaseModel):
    """Current runtime status of the hardware agent."""

    state: State
    message: Optional[str] = Field(None, description="Detail message.")


class PaletteResponse(RootModel[List[PaintItem]]):
    """Complete palette currently available on the agent."""


class DoseItem(BaseModel):
    """A single color‑volume pair for mixing."""

    id: int = Field(..., description="ID of the color, starting from 0.")
    name: str = Field(..., examples=["magenta"])
    volume: float = Field(..., description="Amount of color to inject (mL).")


class DoseRequest(
    RootModel[
        conlist(
            DoseItem,
            min_length=1,
            max_length=6,
        )
    ]
):
    """List of colors to be mixed in one operation."""


class ErrorResponse(BaseModel):
    """Generic error wrapper."""

    error: str = Field(..., description="Error message.")
