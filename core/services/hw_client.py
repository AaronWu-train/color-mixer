# core/services/hw_client.py
import httpx
from typing import Optional, Any, Dict, List
from core.config import settings

# --------------------------------------------------------------------------- #
# Shared AsyncClient instance
# --------------------------------------------------------------------------- #
_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """Lazily instantiate and return a shared AsyncClient."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=settings.hw_agent_base_url,
        )
    return _client


async def close_client() -> None:
    """Close the shared AsyncClient when application shuts down."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# --------------------------------------------------------------------------- #
# API Client Functions
# --------------------------------------------------------------------------- #


async def get_status() -> Dict[str, Any]:
    """Fetch status from the hardware agent."""
    client = await get_client()
    try:
        response = await client.get("/status")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching status: {e.response.status_code} - {e.response.text}")
        return {"state": "error", "message": "Failed to fetch status"}


async def get_color() -> Optional[List[int]]:
    """Fetch RGB color from the hardware agent."""
    client = await get_client()
    try:
        response = await client.get("/color")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching color: {e.response.status_code} - {e.response.text}")
        return None


async def get_palette() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch the color palette from the hardware agent."""
    client = await get_client()
    try:
        response = await client.get("/palette")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error fetching palette: {e.response.status_code} - {e.response.text}")
        return {"palette": []}


async def dose_color(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Send a color dose request to the hardware agent."""
    client = await get_client()
    try:
        response = await client.post(
            "/dose",
            json=items,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Error dosing color: {e.response.status_code} - {e.response.text}")
        return {"state": "error", "message": "Failed to send dose request"}


if __name__ == "__main__":
    import asyncio

    color = asyncio.run(get_color())
    print("get_color:", color)
