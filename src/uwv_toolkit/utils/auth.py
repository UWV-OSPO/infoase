import streamlit as st
from typing import List


def is_authenticated() -> bool:
    """
    Returns whether the user is logged in.

    Returns:
        bool: True if the user is logged in, False otherwise.
    """
    return (
        "authentication_status" in st.session_state
        and st.session_state.authentication_status
    )


def in_usergroup(user_group: List[str]) -> bool:
    """
    Returns whether the user is authenticated and part of the given usergroup.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return (
        is_authenticated()
        and ("username" in st.session_state)
        and (st.session_state.username in user_group)
    )
