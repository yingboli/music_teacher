import streamlit as st

from create_chat import create_chat

if "chat_history" not in st.session_state or len(st.session_state.chat_history) == 0:
    st.session_state.chat_history = [{"role": "assistant", 
                                      "content": "Hello, I'm the AI music teacher! What **topic** would you like to learn?"}]

for message in st.session_state.chat_history:
    st.chat_message(message["role"]).markdown(message["content"])

if "openai_model" not in st.session_state:
    openai_model = "gpt-5.2"
else:
    openai_model = st.session_state.openai_model
    

if message["role"] == "user":
    results = create_chat(
        topic = message["content"],
        profile = st.session_state.profile,
        openai_model = openai_model
    )
    st.session_state.chat_history.append({"role": "assistant", "content": results.content})
    st.chat_message("assistant").markdown(results.content)
    
if prompt := st.chat_input("Enter a topic or ask a question"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})


