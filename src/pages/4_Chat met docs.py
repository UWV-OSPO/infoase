import os
import streamlit as st

from uwv_toolkit.streamlit.page.mixins import ChatMixin, FooterMixin
from uwv_toolkit.db.feedback import FeedbackModel
from modules.streamlit.page.mixin.document_chat_mixin import DocumentChatMixin
from uwv_toolkit.utils import azure_llm, FileExceptionHandler
from modules.smz import SmzDocVector as Vector, SmzDocChain as Chain
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage


class DocChatPage(DocumentChatMixin, FooterMixin, BaseUWVGraphPage):

    def _setup_chain(self):
        """Method to setup the chain object"""
        llm = azure_llm()

        @st.cache_resource(show_spinner="Documenten worden opgehaald en ingeladen...")
        def setup_vector():
            return Vector(enable_cache=True).setup()

        vectordb = setup_vector()
        return Chain(vectorstore=vectordb, llm=llm)


try:
    page = DocChatPage(
        page_config={
            "initial_sidebar_state": "expanded",
            "page_title": "Infoase Document Chat 🤖",
            "page_icon": "🤖",
            "layout": "wide",
        },
        footer={
            "content": "Dit prototype is gemaakt door UWV.",
            "fixed": True,
        },
        chat={
            "enable_source": True,
            "enable_feedback": True,
            "feedback_model": FeedbackModel,
            "chat_history_namespace": "doc_chat_history",
            "documents": Vector.documents,
            "chat_type": "Chat met docs",
        },
    )
    page.show()
except Exception as e:
    FileExceptionHandler.handle(exception=e)
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
