import streamlit as st

from utils import dump_log, load_log

log = load_log()

tabs = st.tabs(st.session_state.all_players)

for i in range(len(st.session_state.all_players)):
    player = st.session_state.all_players[i]
    with tabs[i]:     
        cols = st.columns(2)
        with cols[0]:
            with st.form(key=f"change_score_form_{i}"):
                st.subheader("Change Score")
                score = int(log.loc[log["player"]==player, "score"])
                st.write(f"{player} has {score} ⭐️")
                new_score = st.number_input("Enter the new score:", min_value=0, step=1)
                if st.form_submit_button("Submit"):
                    log.loc[log["player"]==player, "score"] = new_score
                    dump_log(log)
                    st.info(f"Now {player} has {int(log.loc[log["player"]==player, "score"])} ⭐️")
        with cols[1]:
            with st.form(key=f"profile_update_form_{i}"):
                st.subheader("Update Profile")
                st.write(f"{player}'s existing profile: {str(log.loc[log["player"]==player, "profile"].values[0])}")
                new_profile = st.text_area("New profile", height=200)
                if st.form_submit_button("Submit"):
                    log.loc[log["player"]==player, "profile"] = new_profile
                    dump_log(log)
                    st.info(f"{player}'s profile is updated.")
                
        with st.container(width="stretch", horizontal_alignment="right"):
            if st.button("Refresh", key = f"refresh{i}", icon=":material/refresh:"):
                st.cache_data.clear()
                st.rerun()

                st.rerun()
