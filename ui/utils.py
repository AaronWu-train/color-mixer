"""
Utility definitions: enums and color conversions.
"""

from enum import Enum


class CoreState(str, Enum):
    """Operational states from core API."""

    ACCEPTED = "accepted"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


# Map core states to status-pill colors
STATE_COLORS = {
    CoreState.ACCEPTED: "#28a745",
    CoreState.IDLE: "#6c757d",
    CoreState.RUNNING: "#1f77b4",
    CoreState.ERROR: "#dc3545",
}


def hex_to_rgb(hex_code: str) -> list[int]:
    """
    Convert a hex color (e.g. '#AABBCC') to an [R, G, B] list.
    """
    return [int(hex_code[i : i + 2], 16) for i in (1, 3, 5)]
