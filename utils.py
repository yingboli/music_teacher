"""Utility functions"""
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def load_log(ttl:int =600) -> pd.DataFrame:
    """
    Load the log from a Google Spreadsheet
    
    The link to the spreadsheet is in the file: .streamlit/secretes.toml
    Only the first sheet is loaded. 
    In this sheet, make sure the columns names are exactly "player", "score", "profile"

    Also, create st.session_state.all_players

    Parameters
    ----------
    ttl: int
        Number of second the log be in the cache
    
    Returns
    -------
    log: A pandas DataFrame
        Contains information about "player", "score", and "profile"
    """

    conn = st.connection("gsheets_log", type=GSheetsConnection)
    log = conn.read(ttl=ttl)

    if list(log.columns) != ["player", "score", "profile"]:
        raise ValueError("GSheets log has wrong column names. ")

    if len(log) > 0:
        st.session_state.all_players = list(log['player'])
    else:
        st.session_state.all_players = []

    # st.write(st.session_state.all_players)
    # st.write(log)

    
    # # Check if the connection thinks it is a service account
    # conn = st.connection("gsheets", 
    #                      type=GSheetsConnection)
    # if hasattr(conn, "_secrets") and "type" in conn._secrets:
    #     st.write(f"Connection Type: {conn._secrets['type']}")
    # else:
    #     st.error("Connection is running in PUBLIC mode (Service Account secrets not found)")

    return log


def dump_log(log: pd.DataFrame):
    """
    Save the log to a Google Spreadsheet

    The link to the spreadsheet is in the file: .streamlit/secretes.toml

    Parameters
    ----------
    log: A pandas DataFrame, with column names "player", "score", "profile"
    """

    if list(log.columns) != ["player", "score", "profile"]:
        raise ValueError("GSheets log has wrong column names. ")

    conn = st.connection("gsheets_log", type=GSheetsConnection)
    conn.update(data=log)


def register_player(player: str, 
                    profile: Optional[str]=None,
                    ):
    """Log in a new player

    For an exiting play in the log, exact the player's infomation, such as score, profile, admin_status.

    For a new player, write his/her info into the log first.

    Note that "admin" is a special name that has a lot of previleges such as generate quiz sets.
    
    Parameters
    ----------
    player: str
        player's name
    """
    log = load_log()

    ## If the player is new
    if player not in st.session_state.all_players + ["admin"]:
        new_player = pd.Series({"player": player,
                                "score": 0,
                                "profile": profile or ''})
        log = pd.concat([log.T, new_player.T], axis=1).T
        dump_log(log)

    st.session_state.player = player
    if player != "admin":
        st.session_state.score = int(log.loc[log["player"] == player, "score"].values[0])
        st.session_state.profile = log.loc[log["player"] == player, "profile"].values[0]

def save_score_to_log():
    """Save a player's score to log"""
    log = load_log()    
    log.loc[log["player"] == st.session_state.player, "score"] = st.session_state.score
    dump_log(log)

def make_game(num_questions):
    """Make a game out of the inventory"""
    conn = st.connection("gsheets_game_inventory", type=GSheetsConnection)
    game_inventory = conn.read(ttl=0)
    
    if len(game_inventory) >= num_questions:
        game_index = np.random.choice(range(len(game_inventory)), 
                                      size=num_questions, replace=False)
        current_game = game_inventory.iloc[game_index, :]
        new_game_inventory = game_inventory.iloc[[i for i in range(len(game_inventory)) if i not in game_index], :]

        # st.write(len(new_game_inventory))
        conn.update(data=new_game_inventory)
        st.session_state.game_generated = True
        message = "Success!"             
    else:
        current_game = None
        message = "Not enough questions left." 
        st.session_state.game_generated = False
    return current_game, message

def make_surprise():
    """Return a random Youtube video id from the surprise list GSheet"""    
    conn = st.connection("gsheets_surprise_list", type=GSheetsConnection)
    surprises = conn.read(ttl=600)
    random_surprise = surprises.sample(n=1)
    return str(random_surprise['video'].values[0])
