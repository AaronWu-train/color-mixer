"""
Streamlit UI for Color‑Mixer Control Panel.
"""

import streamlit as st
from config import PAGE_CONFIG, CSS
from callbacks import (
    init_session_state,
    copy_sensor_to_target,
    update_target_from_picker,
    toggle_reading,
)
from services import get_core_status, get_sensor_color, start_mixing
from utils import CoreState, STATE_COLORS

# Page setup
st.set_page_config(**PAGE_CONFIG)
st.markdown(CSS, unsafe_allow_html=True)
st.title("Color‑Mixer Control Panel")

# Initialize session state variables
init_session_state()

# --- Core Server Status Panel ---
state, message = get_core_status()
col_info, col_reload = st.columns([4, 1])
with col_info:
    st.subheader("🔌 Core Server Status")
    color = STATE_COLORS.get(state, "#6c757d")
    st.markdown(
        f"<span class='status-pill' style='background-color:{color};'>{state.value.upper()}</span>",
        unsafe_allow_html=True,
    )
    st.code(message or "<no message>")

with col_reload:
    if st.button("🔄", help="Reload server status", use_container_width=True):
        st.experimental_rerun()

st.divider()

# --- Color Display & Controls ---
cols = st.columns([1, 0.15, 1])
# Target color block and picker
with cols[0]:
    st.markdown("### 🎯 Target Color")
    st.markdown(
        f"<div class='color-block' style='background-color: rgb{tuple(st.session_state.target_rgb)};'></div>",
        unsafe_allow_html=True,
    )
    st.write(f"RGB: {tuple(st.session_state.target_rgb)}")
    st.color_picker(
        "Pick target color",
        "#%02x%02x%02x" % tuple(st.session_state.target_rgb),
        key="picker",
        on_change=update_target_from_picker,
    )
# Copy button
with cols[1]:
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)
    st.button("⬅", on_click=copy_sensor_to_target, use_container_width=True)
# Sensor color block and read toggle
with cols[2]:
    st.markdown("### 📷 Sensor Color")
    st.markdown(
        f"<div class='color-block' style='background-color: rgb{tuple(st.session_state.sensor_rgb)};'></div>",
        unsafe_allow_html=True,
    )
    st.write(f"RGB: {tuple(st.session_state.sensor_rgb)}")
    toggle_label = "Read from sensor" if not st.session_state.reading else "⏹ Stop"
    st.button(toggle_label, on_click=toggle_reading)
    if st.session_state.reading:
        st.session_state.sensor_rgb = get_sensor_color()

st.divider()

# --- Start Mixing Button ---
start_cols = st.columns([2, 1, 2])
with start_cols[1]:
    if st.button("🚀 Start Mixing", type="primary", use_container_width=True):
        start_mixing(st.session_state.target_rgb)
        st.success("Mix request submitted!")
