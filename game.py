import ast

import streamlit as st
from xvfbwrapper import Xvfb
from create_quiz import create_quiz
from utils import make_game, save_score_to_log, make_surprise

from music21 import environment
import os

### If served local, comment out this chunk ###
# 1. Start the virtual display
vdisplay = Xvfb()
vdisplay.start()

# Set the path to the MuseScore binary installed via packages.txt
# On Streamlit Cloud (Debian), it's usually at this location:
mscore_path = '/usr/bin/mscore3'

env = environment.Environment()
env['musescoreDirectPNGPath'] = mscore_path
env['musicxmlPath'] = mscore_path

# This tells MuseScore to run in "headless" mode so it doesn't crash 
# looking for a graphical display
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

### The of the chunk ###

def create_one_quiz_question(quizzes, quiz_i):
    """Create one question"""
    quiz = quizzes.iloc[quiz_i, :]
    
    if "already_correct" not in st.session_state:
        st.session_state.already_correct = False

    st.write(f"{quiz_i+1}. {str(quiz['question_text'])}")
    
    vdisplay = Xvfb()
    vdisplay.start()
    try:
        exec(str(quiz['question_code']))
        st.image('game-1.png')
    finally:
        # Always stop the display to free up memory
        vdisplay.stop()

    quiz_choices = ast.literal_eval(str(quiz['choices']))

    cols = st.columns(4)
    for i in range(4):
        if cols[i].button(quiz_choices[i], width="stretch"):
            st.session_state.selected[quiz_i] = i
            if i == int(quiz['answer_index']): 
                if st.session_state.already_correct is False: 
                    st.session_state.score += 1
                    st.toast("⭐️ + 1", duration = 2)
                    st.session_state.already_correct = True
                    # save_score_to_log()
                    st.rerun()
                else:
                    st.write("You have already got it right. Please go to the next question.")
            else:
                if st.session_state.already_correct is False:
                    if st.session_state.hearts > 0:
                        st.session_state.hearts -= 1
                        st.toast("❤️ - 1", duration = 2)
                        st.rerun()
                else:
                    st.write("You have already got it right. Please go to the next question.")

    if st.session_state.selected[quiz_i] < 4:
        with cols[st.session_state.selected[quiz_i]].container(width="stretch", horizontal_alignment="center"):
            if st.session_state.selected[quiz_i] == quiz['answer_index']:
                st.text("✅")   
            else:
                st.text("❌ Please try again.")


def generate_new_game():
    current_game, message = make_game(st.session_state.num_questions)
    if message in ["Not enough questions left."]:
        with st.spinner("Creating the game ..."):
            create_quiz(num_questions = st.session_state.num_questions)
            current_game, message = make_game(st.session_state.num_questions)
        st.session_state.game_generated = True

    return current_game
    
####################################################
if "game_generated" not in st.session_state or st.session_state.game_generated is False:
    st.session_state.quizzes = generate_new_game()

if "current_quiz_i" not in st.session_state or st.session_state.current_quiz_i == -1:
    st.session_state.current_quiz_i = 0
    st.session_state.selected = [4 for i in range(len(st.session_state.quizzes))]

## During the game
if st.session_state.current_quiz_i < len(st.session_state.quizzes) and st.session_state.current_quiz_i >= 0:
    create_one_quiz_question(st.session_state.quizzes, st.session_state.current_quiz_i)

    if st.session_state.already_correct:
        with st.container(width="stretch", horizontal_alignment="right"):
            if st.button("Next question", icon= ":material/arrow_forward:"):
                st.session_state.already_correct = False
                st.session_state.current_quiz_i += 1
                st.rerun()
## At the end of the game
elif st.session_state.current_quiz_i == len(st.session_state.quizzes): 
    save_score_to_log()
    with st.container(width="stretch", horizontal_alignment="center"):
        st.success(f"Awesome {st.session_state.player}! You are done for the day. 😘")
        if st.session_state.hearts > 0:    
            st.markdown(":rainbow-background[:rainbow[Enjoy your surprise.]]")
            video_id = make_surprise() 

            # surprise_prob = {2: 0.5, 10: 0.5, 15: 0.66, 20: 0.75}
            # if np.random.random() < surprise_prob[st.session_state.num_questions]:  
            
            ## For youtube shorts
            # embed_url = f"https://www.youtube.com/embed/{video_id}"
            # st.components.v1.iframe(embed_url, height=600)

            ## For youtube videos
            st.video('https://www.youtube.com/watch?v={video_id}')
 
    st.balloons()

    st.session_state.game_generated = False
    st.session_state.current_quiz_i = -1
    with st.container(width="stretch", horizontal_alignment="right"):
        if st.button("New game", type='primary'):
            st.cache_data.clear()
            st.rerun()
