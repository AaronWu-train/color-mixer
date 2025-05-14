from fastapi import FastAPI
from hw_agent.schemas import (
    MessageResponse, PingResponse, RGBResponse, 
    ResetResponse, DoseRequest, DoseResponse, StatusResponse
)

app = FastAPI(
    title="Color Mixer HW Agent",
    version="0.1.0",
    description="HW Agent 提供感測器讀值與泵浦控制"
)

@app.get("/", response_model=MessageResponse)
async def root():
    return {"message": "Hello, FastAPI in hw_agent!"}

@app.get("/ping", response_model=PingResponse)
async def ping():
    return {"ok": True}

@app.get("/color", response_model=RGBResponse)
async def get_color():
    # TODO: 讀取感測器 raw 數值
    return {"rgb": [255, 255, 255]}

@app.post("/reset", response_model=ResetResponse)
async def reset():
    # TODO: 硬體重置
    return {"ok": True}

@app.post("/dose", response_model=DoseResponse)
async def dose(req: DoseRequest):
    # TODO: 啟動泵浦，傳入 req.recipe
    return {"job_id": "hwjob-1234"}

@app.get("/status", response_model=StatusResponse)
async def status():
    # TODO: 回傳泵浦狀態
    return {"busy": False, "pct": 75}