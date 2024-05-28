import abc
import streamlit as st
import langchain
from typing import Any, Dict

from langchain.cache import SQLiteCache
from modules.layout import Layout
from modules.sidebar import Sidebar
from modules.utils import Utilities

layout_module = Utilities.reload_module("modules.layout")
utils_module = Utilities.reload_module("modules.utils")
sidebar_module = Utilities.reload_module("modules.sidebar")

Layout = layout_module.Layout
Sidebar = sidebar_module.Sidebar
Utilities = utils_module.Utilities


class BasePage(abc.ABC):
    # Config definition
    config: Dict[str, Any]

    sidebar_expanded: bool = True

    # initializer with kwargs as a dict save as self.config
    def __init__(self, **kwargs: Dict[str, Any]):
        self.config = {
            "page_title": "Chat 🤖",
            "page_icon": "💬",
            "caching": False,
            "set_page_config": True,
            "llm_cache_path": "tmp/.langchain.db",
            "initial_sidebar_state": "expanded",
            **kwargs,
        }

        if self.config["set_page_config"]:
            self._set_page_config()

        if self.config["caching"]:
            self._enable_cache()

    def _enable_cache(self):
        """
        Enables caching for the chatbot. Helpful when testing because it will not
        burn tokens.
        """
        langchain.llm_cache = SQLiteCache(database_path=self.config["llm_cache_path"])

    def _page_description(self):
        """
        Override this method to add a description to the page just
        below the page title.
        """
        pass

    def _after_chat(self):
        """
        Override this method to add functionality after the chat.
        """
        pass

    @abc.abstractmethod
    def _page_main(self):
        """
        Override this method to implement the main page.
        """
        pass

    def _page_footer(self):
        """
        Override this method to implement the main page.
        """
        pass

    def _set_page_config(self):
        # Config
        st.set_page_config(
            layout="wide",
            page_icon=self.config["page_icon"],
            page_title=self.config["page_title"],
            initial_sidebar_state=self.config["initial_sidebar_state"],
        )

    def _show_sidebar(self):
        """
        Override this method to add functionality to the sidebar.
        """
        sidebar = Sidebar()
        # Contact
        # sidebar.show_options()
        sidebar.show_caching_state()
        sidebar.contact()

    def show(self) -> None:
        """
        Runs the streamlit page.
        """

        # Instantiate the main components
        layout, utils = Layout(), Utilities()

        self._show_sidebar()

        # Header
        layout.show_header(self.config["page_title"])
        self._page_description()

        # Show main.
        self._page_main()

        # Footer
        self._page_footer()
