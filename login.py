import streamlit as st

from utils import load_log, register_player

log = load_log()

#################################################################
st.write("""## 😃 Hello! Please tell me who you are. 
""") 

st.session_state.ready_to_start = False

cols = st.columns(2)
name1 = cols[0].pills("Are you: ", options=st.session_state.all_players + ["admin"], default=None)
name2 = cols[1].text_input("Or someone else? Put you name here")
profile = cols[1].text_input("Tell me a little bit about yourself. \n\nFor example, a 7 year old boy, or a STEM PhD ")

if name1 is not None:
    player = name1
    register_player(player)
elif cols[1].button("Register new player"):
    if name2 != "": 
        player = name2
        register_player(player, profile=profile)
    else:
        cols[1].write("Hi new player, please tell me your name first. 😅")

# if "score" in st.session_state:
#     st.write(st.session_state.score)

## Welcome message
if "player" in st.session_state:
    if st.session_state.player == "admin":
        password = cols[0].text_input("Admin password")
        if password == st.secrets["admin_password"]:
            st.write("Welcome, admin.")
            st.session_state.ready_to_start = True
            # st.rerun()
        elif password != "":
            st.write("Wrong password. Please try again.")
            
    elif "score" in st.session_state and "player" in st.session_state:
        if st.session_state.score > 0:
            st.write(f"Welcome, {st.session_state.player}! You have {st.session_state.score} ⭐️.")
        elif st.session_state.score == 0:
            st.write(f"Welcome, {st.session_state.player}! Let's play music games and collect ⭐️.")
        st.session_state.ready_to_start = True

## Start button        
if st.session_state.ready_to_start:
    if st.button("Start", icon=":material/start:", type="primary"):
        # if "player" not in st.session_state:
        #     st.write("Please tell me your name first.")
        # else:
        st.session_state.logged_in = True
        st.rerun()
