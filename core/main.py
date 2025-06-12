"""FastAPI entry point for the Color Mixer core service."""

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    BackgroundTasks,
)
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import random, datetime
import asyncio


from .models import (
    RGBColorArray,
    MixRequest,
    MessageResponse,
    StatusResponse,
    State,
)

from .services import hw_client, mix as mix_service
from .services import gamma as gamma_service


# --------------------------------------------------------------------------- #
# Lifespan
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI app."""
    # -- Startup Logic -- #
    app.state.status_state = State.idle
    app.state.status_message = "Core is idle."
    app.state.status_lock = asyncio.Lock()
    app.state.current_mix_task = None  # 用於追蹤當前混色任務的 ayncio.Task

    yield
    # -- Shutdown Logic -- #
    print("Shutting down...")
    await hw_client.close_client()  # Close the shared HTTP client


# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Color Mixer Core API",
    version="0.1.0",
    description="Core API 提供混色演算法與 WebSocket 進度推播",
    validate_response=True,  # 若效率不佳可關閉
    lifespan=lifespan,
)

PRIVATE_NET_REGEX = (  # Only allow private network origins
    r"^https?://"
    r"(?:"
    r"(?:localhost|127\.0\.0\.1)"  # localhost or 127.0.0.1
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"  # 10.x.x.x
    r"|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"  # 172.16–31.x.x
    r"|192\.168\.\d{1,3}\.\d{1,3}"  # 192.168.x.x
    r")"
    r"(?::\d+)?$"  # allowing :port
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=PRIVATE_NET_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
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
    timestamp = datetime.datetime.now().isoformat()
    payload = {
        "state": app.state.status_state,
        "message": f"{app.state.status_message}",
        "timestamp": timestamp,
    }
    return payload


# --------------------------------------------------------------------------- #
# Read‑only endpoints
# --------------------------------------------------------------------------- #
@app.get("/color", response_model=RGBColorArray, tags=["sensor"])
async def read_color() -> RGBColorArray:
    """Read RGB value from the color sensor (scaled 0 - 255)."""
    payload = await hw_client.get_color()
    payload = gamma_service.gamma_correction(payload)
    if payload is None:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Color sensor not available.",
        )

    return payload


# --------------------------------------------------------------------------- #
# WebSocket endpoints
# --------------------------------------------------------------------------- #
@app.websocket("/ws/color")
async def ws_color(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            payload = await hw_client.get_color()
            if payload is None:
                continue  # Skip if sensor is currently not available
            await ws.send_json(payload)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            timestamp = datetime.datetime.now().isoformat()
            payload = {
                "state": app.state.status_state,
                "message": f"{app.state.status_message}",
                "timestamp": timestamp,
            }
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
    if app.state.current_mix_task and not app.state.current_mix_task.done():
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="A mixing session is already in progress.",
        )

    async with app.state.status_lock:
        app.state.status_state = State.accepted
        app.state.status_message = "Mix request accepted."
        app.state.timestamp = datetime.datetime.now().isoformat()
        app.state.current_mix_task = asyncio.create_task(
            mix_service.start_mix(app, req.target.root)
        )

    timestamp = datetime.datetime.now().isoformat()
    return StatusResponse(
        state=State.accepted,
        message="Mix request accepted.",
        timestamp=timestamp,
    )


@app.post("/reset", response_model=MessageResponse, tags=["mix"])
async def reset() -> MessageResponse:
    """Stop the current mixing session and reset state."""

    if not app.state.current_mix_task or app.state.current_mix_task.done():
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="No mixing session is currently in progress.",
        )

    # Cancel the current mixing task
    app.state.current_mix_task.cancel()
    try:
        await app.state.current_mix_task
    except asyncio.CancelledError:
        pass

    return {"ok": True, "message": "Reset complete."}
