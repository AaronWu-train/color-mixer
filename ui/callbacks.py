"""
Streamlit session-state initialization and callbacks.
"""

import streamlit as st
from services import get_sensor_color


def init_session_state():
    """Initialize session-state defaults on first run."""
    if "reading" not in st.session_state:
        st.session_state.reading = False
    if "target_rgb" not in st.session_state:
        st.session_state.target_rgb = [255, 255, 255]
    if "sensor_rgb" not in st.session_state:
        st.session_state.sensor_rgb = get_sensor_color()


def copy_sensor_to_target():
    """Copy the latest sensor RGB into the target."""
    st.session_state.target_rgb = st.session_state.sensor_rgb.copy()


def update_target_from_picker():
    """Sync the color-picker hex into the target RGB."""
    hex_code = st.session_state.picker
    st.session_state.target_rgb = [int(hex_code[i : i + 2], 16) for i in (1, 3, 5)]


def toggle_reading():
    """
    Toggle continuous sensor reading.
    When turning on, trigger a rerun to fetch immediately.
    """
    st.session_state.reading = not st.session_state.reading
    if st.session_state.reading:
        st.rerun()
