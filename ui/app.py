import streamlit as st
import time
import numpy as np

st.title("Color-Mixer UI")

colors = [
    "rgb(255, 0, 0)",
    "rgb(0, 255, 0)",
    "rgb(0, 0, 255)",
    "rgb(255, 255, 0)",
    "rgb(255, 0, 255)",
    "rgb(0, 255, 255)",
]
rgb_values = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
]

if "locked" not in st.session_state:
    st.session_state.locked = False
if "color_index" not in st.session_state:
    st.session_state.color_index = 0

## Below is just for testing purposes. In the final version, this should be removed, and the color which the color sensor detects should be used.
if not st.session_state.locked:
    time.sleep(0.1)
    st.session_state.color_index = (st.session_state.color_index + 1) % len(colors)

current_color = colors[st.session_state.color_index]
current_rgb = rgb_values[st.session_state.color_index]

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"<div style='width:300px; height:300px; background-color:{current_color}; border:2px solid black;'></div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div style='width:300px; height:300px; border:2px solid black; padding:20px;'>
            <h4>R: {current_rgb[0]}</h4>
            <h4>G: {current_rgb[1]}</h4>
            <h4>B: {current_rgb[2]}</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

btn_col1, btn_col2, _ = st.columns([1, 1, 3])

with btn_col1:
    if st.button("Pick Color", use_container_width=True):
        st.session_state.locked = True

with btn_col2:
    if st.button("Start Grading", use_container_width=True):
        st.session_state.locked = False


##try:
##  st.rerun()
##except AttributeError:
##  st.experimental_rerun()
