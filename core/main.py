"""FastAPI entry point for the Color Mixer core service."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    RGBColorArray,
    MixRequest,
    MessageResponse,
    StatusResponse,
    State,
)

import asyncio

app = FastAPI(
    title="Color Mixer Core API",
    version="0.1.0",
    description="Core API 提供混色演算法與 WebSocket 進度推播",
    validate_response=True,  # 若效率不佳可關閉
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=[
        # localhost / 127.0.0.1
        r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?$",
        # 10.x.x.x
        r"^https?://10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}(?::\d+)?$",
        # 172.16.0.0–172.31.255.255
        r"^https?://172\.(?:1[6-9]|2[0-9]|3[0-1])\.(?:[0-9]{1,3}\.)[0-9]{1,3}(?::\d+)?$",
        # 192.168.x.x
        r"^https?://192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3}(?::\d+)?$",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Health & status
# --------------------------------------------------------------------------- #
@app.get("/", response_model=MessageResponse, tags=["health"])
async def ping() -> MessageResponse:
    """Simple health probe."""
    return {"ok": True, "message": "Core API is reachable."}


@app.get("/status", response_model=StatusResponse, tags=["health"])
async def status() -> StatusResponse:
    """Current runtime state of the mixer core."""
    return {"state": State.idle, "message": "Core is idle."}


# --------------------------------------------------------------------------- #
# Read‑only endpoints
# --------------------------------------------------------------------------- #
@app.get("/color", response_model=RGBColorArray, tags=["sensor"])
async def read_color() -> RGBColorArray:
    """Read RGB value from the color sensor (scaled 0 – 255)."""
    # TODO: 讀取換算過的 RGB 數值
    return [0, 255, 255]


# --------------------------------------------------------------------------- #
# WebSocket endpoints
# --------------------------------------------------------------------------- #
@app.websocket("/ws/color")
async def ws_color(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = [0, 255, 255]
            await ws.send_json(payload)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = {"state": State.idle, "message": "Core is idle."}
            await ws.send_json(payload)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


# --------------------------------------------------------------------------- #
# Mutating endpoints
# --------------------------------------------------------------------------- #
@app.post("/mix", response_model=StatusResponse, status_code=202, tags=["mix"])
async def mix(req: MixRequest) -> StatusResponse:
    """Start a color mixing session."""
    # TODO: 呼叫演算法
    return {"state": State.accepted, "message": "Mix request accepted."}


@app.post("/reset", response_model=MessageResponse, tags=["mix"])
async def reset() -> MessageResponse:
    """Stop the current mixing session and reset state."""
    # TODO: 呼叫 hw_agent.reset()
    return {"ok": True, "message": "Reset complete."}
