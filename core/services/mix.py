# core/services/mix.py

import asyncio, datetime
from fastapi import FastAPI


async def start_mix(app: FastAPI, target_rgb: list[int]):
    try:
        async with app.state.status_lock:
            app.state.status_state = "running"
            app.state.status_message = f"Mixing to target RGB: {target_rgb}"
            app.state.timestamp = datetime.datetime.now().isoformat()

        ###################################
        # TODO: DO THE MIXING HERE
        # This is where you would implement the actual mixing logic,
        # such as communicating with hardware to mix colors.
        # For now, we will simulate the mixing process with a sleep.
        await asyncio.sleep(5)
        ###################################

        async with app.state.status_lock:
            app.state.status_state = "finished"
            app.state.status_message = "Mixing completed successfully"
            app.state.timestamp = datetime.datetime.now().isoformat()

    except asyncio.CancelledError:
        async with app.state.status_lock:
            app.state.status_state = "cancelling"
            app.state.status_message = "Mixing session is cancelling"
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
            app.state.status_message = "Core is idle"
            app.state.timestamp = datetime.datetime.now().isoformat()
