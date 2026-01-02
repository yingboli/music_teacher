import streamlit as st

st.title("AI Music Teacher")

cols = st.columns(2)

with cols[0].container(height=300):
    st.subheader("Game")
    st.session_state.num_questions = st.pills("How many questions would you like?", options=[10, 15, 20], default=10)

    if st.button("Start Game!", type="primary"):
        if "current_quiz_i" in st.session_state and st.session_state.current_quiz_i != -1:
            st.write("Game in session. Please finish it. 😅") 
        else:
            st.switch_page("game.py")
            
with cols[1].container(height=300):
    st.subheader("Chat")

    st.chat_message("assistant").markdown("Hello, I'm the AI music teacher! What **topic** would you like to learn?")
    
    if "chat_history" not in st.session_state or len(st.session_state.chat_history) == 0:
        st.session_state.chat_history = [{"role": "assistant", 
                                          "content": "Hello, I'm the AI music teacher! What **topic** would you like to learn?"}]
        
    if prompt := st.chat_input("Enter a topic or ask a question"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.switch_page("chat.py")
        
           
