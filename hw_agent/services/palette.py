from importlib import resources
import json
from pathlib import Path
from typing import List, Dict

_PALETTE_CACHE: List[Dict] | None = None


def get_palette() -> List[Dict]:
    """載入靜態 palette.json，結果快取在記憶體。"""
    global _PALETTE_CACHE
    if _PALETTE_CACHE is None:
        path: Path = resources.files("hw_agent.data").joinpath("palette.json")
        _PALETTE_CACHE = json.loads(path.read_text(encoding="utf-8"))
    return _PALETTE_CACHE
