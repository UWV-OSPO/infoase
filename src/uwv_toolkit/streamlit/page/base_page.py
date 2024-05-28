import abc
import streamlit as st
from typing import Any, Dict
from uwv_toolkit.streamlit.components import Footer


class BasePage(abc.ABC):
    # Config definition
    _config: Dict[str, Any] = {}

    # initializer with kwargs as a dict save as self.config
    def __init__(self, **kwargs: Dict[str, Any]):
        self._config = {
            "page_config": {
                "page_title": "Chat 🤖",
                "page_icon": "🤖",
                "initial_sidebar_state": "expanded",
                "layout": "wide",
            },
            "set_page_config": True,
            **self._config,
            **kwargs,
        }

        if self._config["set_page_config"]:
            st.set_page_config(**self._config["page_config"])

    def _add_css(self, styles: str):
        """
        Override this method to add custom CSS to the page.
        """
        st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

    def _pre_show(self):
        """
        Override this method to add custom code that runs before the page is shown.
        """

    def _show_menu(self):
        """
        Override this method to implement the menu.
        """

    @abc.abstractmethod
    def _show_main(self):
        """
        Override this method to implement the main page.
        """
        st.header(self._config["page_config"]["page_title"])

    def show(self) -> None:
        """
        Runs the streamlit page.
        """
        self._pre_show()
        self._show_menu()
        self._show_main()
