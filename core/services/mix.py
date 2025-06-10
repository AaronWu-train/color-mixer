import asyncio
import datetime
from fastapi import FastAPI
import core.services.hw_client as hw_client
import mixbox
import numpy as np

# 初始與最大總體積設定 (ml)
START_VOLUME = 50
MAX_VOLUME = 150
BATCH_VOLUME = 10  # 每次迭代加料總量
TOLERANCE = 1e-3  # 誤差容忍度


def get_ratio(palette_latent: np.ndarray, target_latent: np.ndarray) -> np.ndarray:
    """
    Solve A x ≈ v in least-squares sense.

    Args:
        palette_latent: (m×n) 矩陣，欄向量為基底 latent vectors。
        target_latent: (m,) 目標 latent vector。

    Returns:
        coeffs: 長度 n 的最小平方係數向量 x。
    """
    coeffs, *_ = np.linalg.lstsq(palette_latent, target_latent, rcond=None)
    return coeffs


async def _set_state(app: FastAPI, state: str, message: str) -> None:
    """
    Safely update the mixing status on app.state with a timestamp.
    """
    async with app.state.status_lock:
        app.state.status_state = state
        app.state.status_message = message
        app.state.timestamp = datetime.datetime.now().isoformat()


async def start_mix(app: FastAPI, target_rgb: list[int]) -> None:
    """
    Iteratively mix colors to reach the target RGB.

    - 初始劑量: START_VOLUME ml
    - 每輪最多加 BATCH_VOLUME ml，直到總量或達到目標。
    """
    try:
        await _set_state(app, "running", f"Mixing to target RGB: {target_rgb}")

        palette = await hw_client.get_palette()
        if not palette:
            await _set_state(app, "error", "Failed to fetch color palette")
            return

        # 1. 生成 latent 矩陣
        target_latent = mixbox.rgb_to_latent(target_rgb)
        palette = sorted(palette, key=lambda c: c["id"])
        palette_latent = np.column_stack(
            mixbox.rgb_to_latent(color["rgb"]) for color in palette
        )  # shape = (m, n)

        # 2. 初始配比與加料
        coeffs = get_ratio(palette_latent, target_latent)
        props = coeffs / np.sum(coeffs)
        init_volumes = np.round(props * START_VOLUME).astype(int)
        recipe = [
            {"id": color["id"], "name": color["name"], "volume": int(vol)}
            for color, vol in zip(palette, init_volumes)
            if vol > 0
        ]
        total_volume = int(np.sum(init_volumes))

        response = await hw_client.dose_color(recipe)
        if response.get("state") != "success":
            await _set_state(
                app, "error", f"Failed to dose colors: {response.get('message','')}"
            )
            return

        # 3. 迭代加料
        while total_volume < MAX_VOLUME:
            status = await hw_client.get_status()
            if status.get("state") != "idle":
                await asyncio.sleep(0.1)
                continue

            current_rgb = await hw_client.get_color()
            if current_rgb is None:
                await _set_state(app, "error", "Failed to fetch current color")
                return

            current_latent = mixbox.rgb_to_latent(current_rgb)
            delta_latent = target_latent - current_latent
            if np.linalg.norm(delta_latent) < TOLERANCE:
                await _set_state(app, "finished", "Target color achieved")
                return

            coeffs_rem = get_ratio(palette_latent, delta_latent)
            props_rem = coeffs_rem / np.sum(coeffs_rem)
            deltas = np.round(props_rem * BATCH_VOLUME).astype(int)

            batch_recipe = [
                {"id": color["id"], "name": color["name"], "volume": int(vol)}
                for color, vol in zip(palette, deltas)
                if vol > 0
            ]
            response = await hw_client.dose_color(batch_recipe)
            if response.get("state") != "success":
                await _set_state(
                    app, "error", f"Failed to dose colors: {response.get('message','')}"
                )
                return

            added = int(np.sum(deltas))
            total_volume += added
            await asyncio.sleep(0.5)

        await _set_state(app, "finished", "Mixing completed successfully")

    except asyncio.CancelledError:
        await _set_state(app, "cancelling", "Mixing session is cancelling")

        await hw_client.halt_pumps()
        raise

    except Exception as e:
        await _set_state(app, "error", f"Error during mixing: {e}")

    finally:
        await asyncio.sleep(3)
        await _set_state(app, "idle", "Core is idle")
