"""FastAPI entry point for the Color Mixer hardware‑agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import random
import asyncio

from hw_agent.models import (
    RGBColorArray,
    DoseRequest,
    MessageResponse,
    PaletteResponse,
    StatusResponse,
    State,
)

from hw_agent.services import palette as palette_service


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
    app.state.current_mix_task = None  # TODO: 用於追蹤當前混色任務的 ayncio.Task

    yield
    # -- Shutdown Logic -- #
    print("Shutting down...")


# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Color Mixer HW Agent",
    version="0.1.0",
    description="Expose sensor readings and pump controls for the color‑mixer hardware.",
    validate_response=True,  # 啟用回應驗證，若效率不佳可關閉
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
    return {"ok": True, "message": "Agent is reachable."}


@app.get("/status", response_model=StatusResponse, tags=["health"])
async def status() -> StatusResponse:
    """Current runtime state of the agent."""
    # TODO: 讀取當前狀態
    return {"state": State.idle, "message": "Agent is idle."}


# --------------------------------------------------------------------------- #
# Read‑only endpoints
# --------------------------------------------------------------------------- #
@app.get("/color", response_model=RGBColorArray, tags=["sensor"])
async def read_color() -> RGBColorArray:
    """Read RGB value from the color sensor (scaled 0 – 255)."""
    # TODO: 讀取換算過的 sRGB 數值
    random_r = random.randint(0, 255)
    random_g = random.randint(0, 255)
    random_b = random.randint(0, 255)
    payload = [random_r, random_g, random_b]
    return payload


@app.get("/palette", response_model=PaletteResponse, tags=["palette"])
async def get_palette() -> PaletteResponse:
    """Return the predefined palette used by the mixer."""
    return palette_service.get_palette()


# --------------------------------------------------------------------------- #
# Mutating endpoints
# --------------------------------------------------------------------------- #
@app.post("/dose", response_model=StatusResponse, status_code=202, tags=["pump"])
async def dose(req: DoseRequest) -> StatusResponse:
    """Enqueue a mix request to the pump controller."""
    # TODO: 啟動泵浦
    return {"state": State.accepted, "message": "Dose request received."}


@app.post("/stop", response_model=MessageResponse, tags=["pump"])
async def stop() -> MessageResponse:
    """Immediately stop all pumps and reset the agent."""
    # TODO: 硬體重置
    return {"ok": True, "message": "Stopped."}
