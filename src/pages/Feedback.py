import streamlit as st
import pandas as pd
from uwv_toolkit.streamlit.page.mixins import FooterMixin, ChatMixin
from uwv_toolkit.db.feedback import FeedbackModel
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage


class FeedbackPage(FooterMixin, BaseUWVGraphPage):
    def _show_main(self):
        st.title(self._config["page_config"]["page_title"])

        FeedbackModel.create_table()

        all_feedback = FeedbackModel.all()

        df = pd.DataFrame([vars(d) for d in all_feedback][::-1])

        st.dataframe(df, height=800)


page = FeedbackPage(
    page_config={
        "initial_sidebar_state": "expanded",
        "page_title": "Feedback 🤩",
        "page_icon": "🤩",
    },
    footer={
        "content": "Dit prototype is gemaakt door UWV.",
        "fixed": True,
    },
)
page.show()
