import abc
import streamlit as st


class BaseStreamlitComponent(abc.ABC):
    """Base class for all components."""

    def _add_styles(self, styles: str) -> None:
        """Add styles to the component."""
        st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

    @abc.abstractmethod
    def show(self):
        """Render the component."""
        pass
