import streamlit as st
from uwv_toolkit.streamlit.components import BaseStreamlitComponent


class Footer(BaseStreamlitComponent):
    # The content of the footer.
    content: str

    # Whether or not to fix the footer at the bottom of the page.
    fixed: bool

    def __init__(
        self,
        content: str = "Dit prototype is gemaakt door UWV.",
        fixed: bool = True,
    ):
        self.content = content
        self.fixed = fixed

    def __styles(self):
        """
        Returns the styles for the footer.
        """

        if self.fixed:
            styles = """
            position: fixed;
            left: 0;
            bottom: 0;
            z-index: 99;
            """
        else:
            styles = ""

        return f"""
        .footer {{
            width: 100%;
            background-color: white;
            color: black;
            text-align: center;
            padding-top: 10px;
            {styles}
        }}
        .footer p {{
            font-size: 12px;
            color: #c0c0c0;
        }}
        .footer a {{
            font-size: 12px;
            color: #c0c0c0;
        }}
        """

    def show(self):
        """
        Renders the footer.
        """

        self._add_styles(self.__styles())

        st.markdown(
            f"""
<div class="footer">
<p>{self.content}</p>
</div>
""",
            unsafe_allow_html=True,
        )
