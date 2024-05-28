import abc
import streamlit as st
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.base_chat_page import BaseChatPage
from modules.streamlit.components import Footer


class ChainChatPage(BaseUWVGraphPage, BaseChatPage, abc.ABC):
    _chat_placeholder: str = "Stel een vraag over een document..."

    _chain = None

    def _setup_before(self):
        pass

    def _setup_jit(self):
        pass

    def _page_main(self):
        self._setup_before()

        self.display_history()
        if user_query := st.chat_input(self._chat_placeholder):
            self.display_msg(user_query, "user")

            with st.spinner("Nadenken over het antwoord..."):
                self._setup_jit()

                if not self._chain:
                    ValueError("Chain not set up.")

                response = self._chain.ask(
                    question=user_query,
                    chat_history=st.session_state[self.namespace]["chat_history"],
                )
            self.display_msg(response, "assistant")

    def _page_footer(self) -> None:
        # pass
        footer = Footer(fixed=True)
        footer.show()
