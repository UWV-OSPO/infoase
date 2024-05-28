import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st
from uwv_toolkit.streamlit.page import BasePage
from uwv_toolkit.utils import load_env, is_authenticated, persistent_path


class BaseAuthenticatedPage(BasePage):
    """This is a class that adds authentication to a page.

    See ./.streamlit/credentials.toml for the credentials.
    """

    _authenticator: stauth.Authenticate

    def __init__(self, *args, **kwargs):
        if (
            "authentication_status" not in st.session_state
            or not st.session_state["authentication_status"]
        ):
            self._config = {
                "page_config": {
                    "initial_sidebar_state": "collapsed",
                },
                **self._config,
                **kwargs,
            }
        super().__init__(*args, **kwargs)

    def _pre_show(self):
        super()._pre_show()

        load_env()
        # credentials_path = os.getenv("CREDENTIALS_PATH", "./.streamlit/credentials.yml")
        credentials_path = f"{persistent_path(os.getenv('CREDENTIALS_PATH'))}/credentials.yml"  # os.getenv("CREDENTIALS_PATH", "./.streamlit/credentials.toml")

        with open(credentials_path, encoding="utf-8") as file:
            config = yaml.load(file, Loader=SafeLoader)

        self._authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            config["preauthorized"],
        )

        self._authenticator.login()

    def _authenticated_show_main(self):
        if is_authenticated():
            self._authenticator.logout(location="sidebar")
            self._show_main()
        elif st.session_state["authentication_status"] is False:
            st.error("Username/password is incorrect")
        elif st.session_state["authentication_status"] is None:
            st.warning("Please enter your username and password")
            for key in st.session_state.keys():
                del st.session_state[key]

    def show(self) -> None:
        """
        Runs the streamlit page.
        """
        self._pre_show()
        self._show_menu()
        self._authenticated_show_main()
