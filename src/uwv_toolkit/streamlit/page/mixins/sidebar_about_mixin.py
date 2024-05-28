import streamlit as st


class SidebarAboutMixin:
    def __init__(self, **kwargs):
        """
        Initializes the SidebarAboutMixin.

        Args:
            **kwargs: Keyword arguments to configure the sidebar about section.
        """
        self._config = {
            "sidebar": {
                "title": "Contact 📮",
                "expanded": False,
                "content": """
                    © Infoase
                """,
            },
            **kwargs,
        }

        super().__init__(**kwargs)

    def show(self) -> None:
        """
        Displays the page content and the sidebar about section, if configured.

        Returns:
            None
        """
        super().show()

        if "sidebar" in self._config and self._config["sidebar"]:
            cfg = self._config["sidebar"]
            with st.sidebar:
                if "title" in cfg:
                    with st.expander(cfg["title"], expanded=cfg["expanded"]):
                        st.markdown(cfg["content"])
                else:
                    st.markdown(cfg["content"])
