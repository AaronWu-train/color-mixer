"""FastAPI entry point for the Color Mixer hardware‑agent."""

from fastapi import (
    FastAPI,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import random, datetime
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
from hw_agent.services import dose as dose_service
from hw_agent.services import color as color_service


# --------------------------------------------------------------------------- #
# Lifespan
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI app."""
    # -- Startup Logic -- #
    app.state.status_state = State.idle
    app.state.status_message = "Hardware Agent is idle."
    app.state.status_lock = asyncio.Lock()
    app.state.current_dose_task = None  # 用於追蹤當前 Dose 任務的 ayncio.Task

    yield
    # -- Shutdown Logic -- #
    print("Shutting down...")


# --------------------------------------------------------------------------- #
# FastAPI app
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Color Mixer HW Agent",
    version="0.1.0",
    description="Expose sensor readings and pump controls for the color-mixer hardware.",
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
    """Read sRGB value from the color sensor (scaled 0 - 255)."""
    r, g, b = await color_service.getColor()
    payload = [r, g, b]
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
    """Start a pump dosing session."""
    if app.state.current_dose_task and not app.state.current_dose_task.done():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A dosing session is already in progress.",
        )

    async with app.state.status_lock:
        app.state.status_state = State.running
        app.state.status_message = f"Starting dosing with recipe: {req}"
        app.state.timestamp = datetime.datetime.now().isoformat()
        app.state.current_dose_task = asyncio.create_task(
            dose_service.start_dose(app, req.recipe)
        )

    return {"state": State.accepted, "message": "Dose request received."}


@app.post("/stop", response_model=MessageResponse, tags=["pump"])
async def stop() -> MessageResponse:
    """Immediately stop all pumps and reset the agent."""
    # TODO: 硬體重置
    return {"ok": True, "message": "Stopped."}
