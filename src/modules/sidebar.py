import streamlit as st
from langchain.globals import get_llm_cache


class Sidebar:
    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4", "azure"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def show_caching_state():
        cache = get_llm_cache()
        with st.sidebar:
            if cache is None:
                st.info("Caching is disabled.")
            else:
                st.success("Caching is enabled.")

    @staticmethod
    def contact():
        with st.sidebar.expander("📬 Contact"):
            st.write("**© Infoase 2024**")

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state.model_name = model

    def moderation_checkbox(self):
        helptext = "Enable moderation to prevent harmful content from being generated, see https://platform.openai.com/docs/guides/moderation."
        st.session_state.moderation = st.checkbox(
            "Moderation", value=False, help=helptext
        )

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state.temperature = temperature

    def show_options(self):
        with st.sidebar.expander("🛠️ Settings", expanded=False):
            st.write("Changes are applied immediately.")
            self.reset_chat_button()
            self.model_selector()
            self.temperature_slider()
            self.moderation_checkbox()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)
