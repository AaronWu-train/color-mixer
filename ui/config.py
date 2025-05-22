"""
Global configuration for Color‑Mixer UI.
"""

# Base URL of the core API
API_BASE = "http://localhost:8000"

# Streamlit page settings
PAGE_CONFIG = {
    "page_title": "Color‑Mixer",
    "page_icon": "🎨",
    "layout": "centered",
}

# Custom CSS for color blocks and status pill
CSS = """
<style>
.color-block {
    width: 220px;
    height: 220px;
    border: 3px solid #000;
    border-radius: 12px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.25);
}
.status-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
}
</style>
"""
