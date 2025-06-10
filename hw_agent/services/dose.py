# hw_agent/services/dose.py

import asyncio, datetime
from fastapi import FastAPI
from ..models import (
    RGBColorArray,
    DoseRequest,
    DoseItem,
    MessageResponse,
    PaletteResponse,
    StatusResponse,
    State,
)

from ..drivers import pump as pump_driver


async def start_dose(app: FastAPI, recipe: list[DoseItem]) -> None:
    tasks = []
    try:
        async with app.state.status_lock:
            app.state.status_state = State.running
            app.state.status_message = f"Dosing paints with recipe: {recipe}"
            app.state.timestamp = datetime.datetime.now().isoformat()

        tasks = [
            asyncio.create_task(pump_driver.startPump(item.id, item.volume))
            for item in recipe
        ]

        await asyncio.gather(*tasks)

        async with app.state.status_lock:
            app.state.status_state = "finished"
            app.state.status_message = "Dosing completed successfully"
            app.state.timestamp = datetime.datetime.now().isoformat()

    except asyncio.CancelledError:
        async with app.state.status_lock:
            app.state.status_state = "cancelling"
            app.state.status_message = "Dosing session is cancelling"
            app.state.timestamp = datetime.datetime.now().isoformat()

        for t in tasks:
            if not t.done():
                t.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        await pump_driver.haltPumpAll()
        print("所有 pump 任務已取消")

    except Exception as e:
        print(str(e))
        async with app.state.status_lock:
            app.state.status_state = "error"
            app.state.status_message = f"Error during mixing: {str(e)}"
            app.state.timestamp = datetime.datetime.now().isoformat()

        await pump_driver.haltPumpAll()

    finally:

        await asyncio.sleep(3)  # Hold finished state for 3 seconds

        async with app.state.status_lock:
            app.state.status_state = "idle"
            app.state.status_message = "Hardware Agent is idle"
            app.state.timestamp = datetime.datetime.now().isoformat()
