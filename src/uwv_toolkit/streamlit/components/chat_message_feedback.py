import streamlit as st
from typing import List

from uwv_toolkit.db import BaseModel
from uwv_toolkit.streamlit.components.base_streamlit_component import (
    BaseStreamlitComponent,
)


class ChatMessageFeedback(BaseStreamlitComponent):

    _response: str
    _messages: List[dict]
    _model_cls: BaseModel
    _extra: dict
    _chat_type: str

    def __init__(
        self, extra: dict, chat_type: str, messages: List[dict], model_cls: BaseModel
    ):
        self._extra = extra
        self._messages = messages
        self._chat_type = chat_type
        self._model_cls = model_cls
        self._model_cls.create_table()

    def show(self):
        """
        Displays a feedback message for the chatbot.

        Example:
            feedback = ChatMessageFeedback()
            feedback.show()
        """

        placeholder = st.empty()

        def _submit_feedback():
            self._model_cls(
                feedback_type=st.session_state.fb_positive,
                ground_truth=st.session_state.fb_answer,
                remark=st.session_state.fb_remark,
                authenticated_user=st.session_state.name,
                chat_history=str(self._messages),
                extra=str(self._extra),
                chat_type=str(self._chat_type),
                context=str(self._extra["context"]),
                user_email=st.session_state.fb_email,
            ).save()

            # Hide the form after submission
            st.toast("Bedankt voor je feedback!", icon="👍")
            st.balloons()
            placeholder.empty()

        # submitted = False
        with placeholder:
            with st.expander("👂 Feedback", expanded=False):
                with st.form(key="feedback_form", border=False, clear_on_submit=True):
                    st.markdown(
                        "Wat vond je van het antwoord? Jouw feedback helpt ons de kwaliteit van de antwoorden te verhogen."
                    )

                    st.radio(
                        "Was dit een goed antwoord?",
                        ["👍 Ja", "👎 Nee"],
                        horizontal=True,
                        key="fb_positive",
                    )

                    st.text_area(
                        "Als het geen goed antwoord was: wat had het antwoord volgens jou moeten zijn?",
                        height=100,
                        help="Hoe specifieker je feedback, des te beter we kunnen leren van je feedback.",
                        key="fb_answer",
                    )
                    st.text_area(
                        "Heb je nog een opmerking?",
                        height=100,
                        help="Hoe specifieker je feedback, des te beter we kunnen leren van je feedback.",
                        key="fb_remark",
                    )
                    st.text_input(
                        "Je e-mailadres (optioneel)",
                        help="We vragen je e-mail adres om je feedback te kunnen opvolgen. Dit is optioneel.",
                        key="fb_email",
                    )

                    st.session_state.feedback_submitted = st.form_submit_button(
                        "Verstuur feedback", on_click=_submit_feedback
                    )
