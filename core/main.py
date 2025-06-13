from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from core.schemas import (
    MessageResponse, PingResponse, 
    MixRequest, MixResponse, ResetResponse,
    WSColorResponse, WSMixStarted, WSMixProgress, WSMixFinished, WSMixError
)
import asyncio
from uuid import uuid4

app = FastAPI(
    title="Color Mixer Core API",
    version="0.1.0",
    description="Core API 提供混色演算法與 WebSocket 進度推播",
    validate_response=True  # 啟用回應驗證，若效率不佳可關閉
)

@app.get("/", response_model=MessageResponse)
async def root():
    return {"message": "Hello, FastAPI in core!"}

@app.get("/ping", response_model=PingResponse)
async def ping():
    return {"ok": True}

@app.post("/mix", response_model=MixResponse)
async def mix(req: MixRequest):
    session = uuid4()
    # TODO: 啟動後端混色流程（非同步傳給 hw_agent）
    return {"session": session}

@app.post("/reset", response_model=ResetResponse)
async def reset():
    # TODO: 呼叫 hw_agent.reset()
    return {"ok": True}

@app.websocket("/ws/color")
async def ws_color(ws: WebSocket):
    await ws.accept()
    while True:
        # TODO: call hw_agent.get_color() → raw → scale 0–255
        push = WSColorResponse(rgb=[128, 64, 32])
        await ws.send_json(push.dict())
        await asyncio.sleep(0.5)

@app.websocket("/ws/mix/{session}")
async def ws_mix(ws: WebSocket, session: str):
    await ws.accept()
    # 範例流程
    await ws.send_json(WSMixStarted(recipe={"r":10.0,"g":5.0,"b":2.0}).dict())
    for pct in range(0, 101, 20):
        await ws.send_json(WSMixProgress(pct=pct).dict())
        await asyncio.sleep(0.2)
    await ws.send_json(WSMixFinished(deltaE=1.23, final_rgb=[128,128,128]).dict())

    