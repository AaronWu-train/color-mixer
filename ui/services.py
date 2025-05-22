"""
Core API services: HTTP requests to the backend.
"""

import requests
from utils import CoreState

from config import API_BASE


def get_core_status() -> tuple[CoreState, str]:
    """Fetch core server status and message."""
    try:
        response = requests.get(f"{API_BASE}/status", timeout=1)
        response.raise_for_status()
        data = response.json()
        return CoreState(data.get("state", "error")), data.get("message", "")
    except Exception as e:
        return CoreState.ERROR, f"Status error: {e}"


def get_sensor_color() -> list[int]:
    """Fetch the latest sensor RGB reading."""
    try:
        response = requests.get(f"{API_BASE}/color", timeout=1)
        response.raise_for_status()
        return response.json().get("rgb", [0, 0, 0])
    except Exception:
        return [0, 0, 0]


def start_mixing(target_rgb: list[int]) -> None:
    """Send a mix request with target RGB."""
    try:
        requests.post(f"{API_BASE}/mix", json={"target": target_rgb}, timeout=1)
    except Exception:
        pass  # UI will show any status errors on next refresh
