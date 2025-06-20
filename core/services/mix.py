import asyncio
import datetime
from fastapi import FastAPI
import core.services.hw_client as hw_client
import mixbox
import numpy as np
from scipy.optimize import nnls

# 初始與最大總體積設定 (ml)
START_VOLUME = 60
MAX_VOLUME = 110
BATCH_VOLUME = 5  # 每次迭代加料總量
TOLERANCE = 0.03  # 誤差容忍度


def get_ratio(palette_latent: np.ndarray, target_latent: np.ndarray) -> np.ndarray:
    """
    Solve A x ≈ v in least-squares sense.

    Args:
        palette_latent: (m×n) 矩陣，欄向量為基底 latent vectors。
        target_latent: (m,) 目標 latent vector。

    Returns:
        coeffs: 長度 n 的最小平方係數向量 x。
    """
    coeffs, _ = nnls(palette_latent, target_latent)
    return coeffs


async def _set_state(app: FastAPI, state: str, message: str) -> None:
    """
    Safely update the mixing status on app.state with a timestamp.
    """
    print(f"Setting state to {state} with message: {message}")
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
    print(f"Starting mix to target RGB: {target_rgb}")
    try:
        await _set_state(app, "running", f"Mixing to target RGB: {target_rgb}")

        palette = await hw_client.get_palette()
        if not palette:
            await _set_state(app, "error", "Failed to fetch color palette")
            return

        # 1. 生成 latent 矩陣
        target_latent = np.array(mixbox.rgb_to_latent(target_rgb))
        palette = sorted(palette, key=lambda c: c["id"])
        palette_latent = np.column_stack(
            [mixbox.rgb_to_latent(color["rgb"]) for color in palette]
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
        print(f"Initial recipe: {recipe}")
        total_volume = int(np.sum(init_volumes))

        response = await hw_client.dose_color(recipe)

        # 3. 迭代加料
        while total_volume < MAX_VOLUME:
            status = await hw_client.get_status()
            if status.get("state") != "idle":
                await asyncio.sleep(0.1)
                continue
            print(f"Current total volume: {total_volume} ml")

            current_rgb = await hw_client.get_color()
            if current_rgb is None:
                print("Failed to fetch current color")
                await _set_state(app, "error", "Failed to fetch current color")
                return
            print(f"Current RGB: {current_rgb}")

            current_latent = np.array(mixbox.rgb_to_latent(current_rgb))
            delta_latent = target_latent - current_latent
            print(f"Delta latent vector: {delta_latent}", np.linalg.norm(delta_latent))
            if np.linalg.norm(delta_latent) < TOLERANCE:
                print("Target color reached within tolerance.")
                break

            cur_palette_latent = np.hstack(
                [palette_latent, current_latent[:, np.newaxis]]
            )

            coeffs_rem = get_ratio(cur_palette_latent, delta_latent)
            props_rem = coeffs_rem / np.sum(coeffs_rem)
            print(f"Remaining proportions: {props_rem}")

            batch_volume = BATCH_VOLUME
            if props_rem[-1] != 0:
                batch_volume = min(BATCH_VOLUME, total_volume / props_rem[-1])
                print(
                    f"Adjusting batch volume to {batch_volume} ml based on current color"
                )

            batch_volume = min(batch_volume, MAX_VOLUME - total_volume)
            deltas = np.round(props_rem[:-1] * batch_volume, decimals=3)

            batch_recipe = [
                {"id": color["id"], "name": color["name"], "volume": float(vol)}
                for color, vol in zip(palette, deltas)
                if vol > 0
            ]
            print(f"Batch recipe: {batch_recipe}")
            await _set_state(
                app,
                "running",
                f"Mixing batch: {batch_recipe} (total volume: {total_volume + int(np.sum(deltas))} ml)",
            )

            response = await hw_client.dose_color(batch_recipe)
            if response.get("state") != "accepted":
                await _set_state(
                    app, "error", f"Failed to dose colors: {response.get('message','')}"
                )
                return

            added = int(np.sum(deltas))
            total_volume += added
            await asyncio.sleep(0.5)

        while True:
            status = await hw_client.get_status()
            if status.get("state") == "idle":
                break
            await _set_state(
                app,
                "running",
                f"Waiting for pumps to finish, current state: {status.get('state')}",
            )
            # print(f"Waiting for pumps to finish, current state: {status.get('state')}")
            await asyncio.sleep(0.1)

        await _set_state(app, "finished", "Mixing completed successfully")

    except asyncio.CancelledError:
        print("Mixing session was cancelled")
        await _set_state(app, "cancelling", "Mixing session is cancelling")

        await hw_client.halt_pumps()
        raise

    except Exception as e:
        print(f"Error during mixing: {e}")
        await _set_state(app, "error", f"Error during mixing: {e}")

    finally:
        await asyncio.sleep(3)
        await _set_state(app, "idle", "Core is idle")
