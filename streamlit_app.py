
import streamlit as st





st.set_page_config(page_title="AI Music Teacher", page_icon="🎼")

player_pages = [
    st.Page(
        "home.py",
        title="Home",
        icon=":material/home:"
    ),    
    st.Page(
        "game.py",
        title="Game",
        icon=":material/quiz:"
    ),    
    st.Page(
        "chat.py",
        title="Chat",
        icon=":material/chat:"
    ),
]

admin_pages = [
    st.Page(
        "generate_games.py",
        title="Generate Game Inventory",
        icon=":material/wand_stars:"
    ),    
    st.Page(
        "manage_players.py",
        title="Manager Players",
        icon=":material/manage_accounts:"
    ),
    st.Page(
        "settings.py",
        title="Settings",
        icon=":material/settings:"
    ),
]

login_page = st.Page("login.py", title="Log in", icon=":material/login:")
logout_page = st.Page("logout.py", title="Log out", icon=":material/logout:")
####################################################
## Login and Logout
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if st.session_state.player == "admin":
        page = st.navigation(admin_pages+[logout_page]) 
    else:
        page = st.navigation(player_pages+[logout_page])     
        if "hearts" not in st.session_state:
            st.session_state.hearts = 3
            
        with st.sidebar.container(height=50, border=False):
            st.write(f"{st.session_state.player}: {st.session_state.score} ⭐️  {st.session_state.hearts} ❤️")

        if page.title == "Chat":
            with st.sidebar.container(height=350, border=False):
                model1 = st.selectbox("Select OpenAI model",
                                      ["gpt-5.2", "gpt-4o"])
                model2 = st.text_input("Something else?")
                if st.button("Submit"):
                    if model2 != "":
                        st.session_state.openai_model = model2
                    else:
                        st.session_state.openai_model = model1
                    st.info(f"{st.session_state.openai_model} in use for chats.")
            
else:
    page = st.navigation([login_page])

page.run()

