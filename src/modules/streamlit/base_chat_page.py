import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage


class BaseChatPage:
    namespace: str = "chat"

    def init_history(self):
        if not self.namespace in st.session_state:
            st.session_state[self.namespace] = {}
        if (
            "messages" not in st.session_state[self.namespace]
            or len(st.session_state[self.namespace]["messages"]) == 0
        ):
            st.session_state[self.namespace]["messages"] = [
                {"role": "assistant", "content": "Hi, wat kan ik voor je betekenen?"}
            ]
        if (
            "chat_history" not in st.session_state[self.namespace]
            or len(st.session_state[self.namespace]["chat_history"]) == 0
        ):
            st.session_state[self.namespace]["chat_history"] = [
                AIMessage(content="Hi, wat kan ik voor je betekenen?")
            ]

    def display_history(self):

        if (
            self.namespace in st.session_state
            and len(st.session_state[self.namespace]["chat_history"]) > 1
            and st.button("Begin een lege chat", key="clear_chat")
        ):
            st.session_state[self.namespace]["chat_history"] = []
            st.session_state[self.namespace]["messages"] = []

        self.init_history()

        for message in st.session_state[self.namespace]["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def display_msg(self, msg: str, author: str):
        """Method to display message on the UI

        Args:
            msg (str): message to display
            author (str): author of the message -user/assistant
        """

        st.session_state[self.namespace]["messages"].append(
            {"role": author, "content": msg}
        )
        if author == "user":
            st.session_state[self.namespace]["chat_history"].append(
                HumanMessage(content=msg)
            )
        else:
            st.session_state[self.namespace]["chat_history"].append(
                AIMessage(content=msg)
            )

        st.chat_message(author).write(msg)
