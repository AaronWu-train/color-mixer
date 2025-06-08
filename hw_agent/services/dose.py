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


async def start_dose(app: FastAPI, recipe: list[DoseItem]) -> None:
    try:
        async with app.state.status_lock:
            app.state.status_state = State.running
            app.state.status_message = f"Dosing paints with recipe: {recipe}"
            app.state.timestamp = datetime.datetime.now().isoformat()

        ###################################
        # TODO: DO THE DOSING HERE
        # This is where you would implement the actual dosing logic,
        # such as calling drivers or hardware interfaces to control pumps.
        # For now, we will simulate the mixing process with a sleep.
        await asyncio.sleep(5)
        ###################################

        async with app.state.status_lock:
            app.state.status_state = "finished"
            app.state.status_message = "Dosing completed successfully"
            app.state.timestamp = datetime.datetime.now().isoformat()

    except asyncio.CancelledError:
        async with app.state.status_lock:
            app.state.status_state = "cancelling"
            app.state.status_message = "Dosing session is cancelling"
            app.state.timestamp = datetime.datetime.now().isoformat()

        # TODO: Handle cancellation gracefully
        # TODO: Call hardware to stop mixing

        raise

    except Exception as e:
        async with app.state.status_lock:
            app.state.status_state = "error"
            app.state.status_message = f"Error during mixing: {str(e)}"
            app.state.timestamp = datetime.datetime.now().isoformat()

    finally:
        await asyncio.sleep(3)  # Hold finished state for 3 seconds

        async with app.state.status_lock:
            app.state.status_state = "idle"
            app.state.status_message = "Hardware Agent is idle"
            app.state.timestamp = datetime.datetime.now().isoformat()
