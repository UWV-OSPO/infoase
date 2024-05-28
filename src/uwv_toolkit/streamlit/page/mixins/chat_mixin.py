import streamlit as st
from typing import Union, Iterator
from streamlit.delta_generator import DeltaGenerator
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage
from uwv_toolkit.db.feedback import FeedbackModel
from uwv_toolkit.streamlit.components import (
    ChatMessageFeedback,
)
from uwv_toolkit.utils import deep_update


class ChatMixin:

    _chat_config = {
        "chat": {
            "enable_feedback": True,
            "feedback_model": None,
            "chat_history_namespace": "default_chat_history",
            "chat_type": None,
        }
    }

    def __init__(self, **kwargs):
        """
        Initializes the ChatMixin.

        Args:
            **kwargs: Keyword arguments to configure the Chat.
        """
        self._config = deep_update(
            self._chat_config,
            kwargs,
        )

        if not self._config["chat"]["feedback_model"]:
            raise ValueError("Feedback model is required")

        if not self._config["chat"]["chat_type"]:
            raise ValueError("Instance type is required (Prod/Dev)")

        if not self._config["chat"]["chat_history_namespace"] in st.session_state:
            st.session_state[self._config["chat"]["chat_history_namespace"]] = {}
            self.init_history()

        super().__init__(**self._config)

    def _set_chat_session_state(self, key: str, value: Union[str, list, dict]):
        st.session_state[self._config["chat"]["chat_history_namespace"]][key] = value

    def _get_chat_session_state(self, key: str = None):
        if key is None:
            return st.session_state[self._config["chat"]["chat_history_namespace"]]
        else:
            return st.session_state[self._config["chat"]["chat_history_namespace"]][key]

    def init_history(self):
        if "messages" not in self._get_chat_session_state():
            self._set_chat_session_state(
                "messages",
                [{"role": "assistant", "content": "Hi, wat kan ik voor je betekenen?"}],
            )
        if "chat_history" not in self._get_chat_session_state():
            self._set_chat_session_state(
                "chat_history", [AIMessage(content="Hi, wat kan ik voor je betekenen?")]
            )

        if "feedback_submitted" not in self._get_chat_session_state():
            self._set_chat_session_state("feedback_submitted", False)

    def _display_feedback_expander(
        self, raw_response: dict, chat_type: str, container: DeltaGenerator
    ):

        if (
            container
            and self._config["chat"]["enable_feedback"]
            and not self._get_chat_session_state("feedback_submitted")
            and len(self._get_chat_session_state("messages")) > 1
            and self._get_chat_session_state("messages")[-1]["role"] == "assistant"
        ):
            with container:
                ChatMessageFeedback(
                    extra=raw_response,
                    chat_type=chat_type,
                    messages=self._get_chat_session_state("messages"),
                    model_cls=FeedbackModel,
                ).show()

    def _display_sources_expander(
        self, container: DeltaGenerator, sources: list
    ) -> None:
        """
        Method to display sources in an expander.

        Args:
            chat_message_block: the chat message block
            sources: list of sources

        Returns:
            None
        """
        messages = self._get_chat_session_state("messages")

        if (
            container is not None
            and sources is not None
            and self._config["chat"]["enable_source"]
            and len(messages) > 1
            and messages[-1]["role"] == "assistant"
        ):
            with container:
                with st.expander("🔗 Bekijk bronnen:"):
                    st.info(
                        f"Er zijn {len(sources)} relevante paragrafen in de documenten gevonden.",
                        icon="ℹ️",
                    )

                    for source in sources:
                        with st.container(border=True):
                            st.markdown(f"**Bron:** {source.metadata['source']}")
                            st.markdown(f"**Paragraaf:** {source.page_content}")

    def _display_debug(self, container: DeltaGenerator, debug: str) -> None:
        """
        Method to display debug information in an expander.

        Args:
            container: the chat message block
            debug: dict of debug information

        Returns:
            None
        """
        if container is not None and debug is not None:
            with container:
                with st.expander("🔍 Debug informatie"):
                    st.code(debug)

    def display_history(self):
        self.init_history()

        last_message = None
        messages = self._get_chat_session_state("messages")
        for message in messages:
            last_message = st.chat_message(message["role"])
            with last_message:
                st.markdown(message["content"])

    def display_msg(self, msg: Union[str, Iterator], author: str) -> str:
        """Method to display message on the UI

        Args:
            msg (str): message to display
            author (str): author of the message -user/assistant

        Important: The stream needs to be a dict with response (streaming chat) and context keys (sources).

        Returns:
            str: message to display
        """

        self._set_chat_session_state("feedback_submitted", False)
        if author == "user":
            st.session_state[self._config["chat"]["chat_history_namespace"]][
                "chat_history"
            ].append(HumanMessage(content=msg))
            st.session_state[self._config["chat"]["chat_history_namespace"]][
                "messages"
            ].append({"role": author, "content": msg})
            st.chat_message("user").write(msg)
            return msg

        # Handle the assistance message.
        chat_message_block = st.chat_message("assistant")

        chat_message_block.write(msg["response"])
        st.session_state[self._config["chat"]["chat_history_namespace"]][
            "chat_history"
        ].append(AIMessage(content=msg["response"]))
        st.session_state[self._config["chat"]["chat_history_namespace"]][
            "messages"
        ].append({"role": author, "content": msg["response"]})

        self._display_feedback_expander(
            raw_response=msg,
            chat_type=self._config["chat"]["chat_type"],
            container=chat_message_block,
        )

        self._display_sources_expander(chat_message_block, msg["context"])

        debug_information = msg["debug"]
        if "cypher" in msg:
            debug_information += "\n\n##################\nGENERATED CYPHER:\n"
            debug_information += msg.get("cypher")

        if "contextualised_question" in msg:
            debug_information += "\n\n##################\nCONTEXTUALISED QUESTION:\n"
            debug_information += msg.get("contextualised_question")

        self._display_debug(chat_message_block, debug_information)

        return msg
