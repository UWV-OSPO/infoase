import abc
import streamlit as st

from uwv_toolkit.streamlit.page.mixins import ChatMixin
from uwv_toolkit.streamlit.components import (
    DownloadFileLink,
)
from uwv_toolkit.utils import deep_update


class DocumentChatMixin(ChatMixin):

    _chat_config = {
        "chat": {
            "enable_feedback": True,
            "feedback_model": None,
            "chat_history_namespace": "default_chat_history",
            "documents": None,
        }
    }

    def _document_expander(self):
        """
        Creates an expander which shows the documents that are available for querying.
        """

        if not self._config["chat"]["documents"]:
            raise ValueError(
                "No documents in the config, please provide documents via config['chat']['documents']"
            )

        with st.expander("ℹ️ Over de documenten"):
            st.markdown("De volgende documenten zijn bevraagbaar:")

            @st.cache_resource
            def show_documents():
                for doc in self._config["chat"]["documents"]:
                    DownloadFileLink(filepath=doc, prepend="- ").show()

            show_documents()

            st.markdown(
                "Je kunt de geindexeerde bronnen verversen, doe dit alleen als de documenten zijn aangepast."
            )
            if st.button("Documenten opnieuw indexeren"):
                st.cache_resource.clear()

    def _show_chat(self, chain):
        """
        Shows the chat interface.
        """
        self.display_history()

        if user_query := st.chat_input("Stel een vraag over een document..."):
            self.display_msg(user_query, "user")

            st.session_state.logs = ""

            answer = chain.ask(
                question=user_query,
                chat_history=self._get_chat_session_state("chat_history"),
            )

            self.display_msg(answer, "assistant")

    def _setup_chain(self):
        """
        Creates the chain object.
        """
        raise NotImplementedError("Please implement this method in the subclass.")

    def _show_main(self):

        super()._show_main()

        st.markdown("Op deze pagina is het mogelijk om te chatten met documenten.")

        self._document_expander()

        st.markdown("---")

        chain = self._setup_chain()
        self._show_chat(chain)
