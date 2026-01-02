import time

import streamlit as st

from create_quiz import create_quiz

st.title("Generate Game Inventory")


cols = st.columns(2)

with cols[0].container(height=300, border=False):
    st.session_state.num_questions = st.pills("How many questions would you like?", options=[100, 200, 500], default=100)
    
    st.write("Topics")
    st.session_state.quiz_topics = []
    if st.checkbox("Pitches", value=True):
        st.session_state.quiz_topics.append('pitch')
    if st.checkbox("Durations", value=True):
        st.session_state.quiz_topics.append('duration')
    if st.checkbox("Time signatures", value=True):
        st.session_state.quiz_topics.append('time_signature')
    if st.checkbox("Major scales", value=False):
        st.session_state.quiz_topics.append('major_scale')
    if st.checkbox("Signs", value=False):
        st.session_state.quiz_topics.append('signs')

with cols[1].container(height=300, border=False):
    message = st.text_area("Additional instructions", 
                                 value = """If pitch is among the syllabus topics, then about 50% of the time, the question is about the pitch of a note. Please spread out them randomly. Limit the pitch to be inside the range from C2 to C6.""",
                               height=200)

    openai_model = st.selectbox("Which OpenAI model would you like to use?",
                                ["gpt-5.2", "gpt-4o"])

if st.button("Generate", type="primary"):
    with st.spinner("Creating game inventory..."):
        start_time = time.time()
        create_quiz(topics = st.session_state.quiz_topics,
                    num_questions = st.session_state.num_questions,
                    message=message, openai_model=openai_model)
        runtime = time.time() - start_time
        st.success(f"Game inventory generated. It took {openai_model} model {round(runtime)} seconds.")

st.info("Generating 100 questions takes about 3 minutes.")
