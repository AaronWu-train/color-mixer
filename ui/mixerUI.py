import streamlit as st;

st.title("Mixer UI")
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div style='width:300px; height:300px; border: 2px solid black;'></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div style='width:300px; height:300px; border: 2px solid black;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("color picked"):
        st.write("color picked")
with col2:
    if st.button("start color grading"):
        st.write("start color grading")


