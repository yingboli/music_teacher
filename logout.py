import streamlit as st

st.session_state.logged_in = False
st.session_state.game_generated = False
if "chat_history" in st.session_state:
    st.session_state.chat_history = []

st.rerun()
