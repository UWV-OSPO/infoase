import os
import base64
import streamlit as st
from uwv_toolkit.streamlit.components.base_streamlit_component import (
    BaseStreamlitComponent,
)


class DownloadFileLink(BaseStreamlitComponent):

    filepath: str

    def __init__(self, filepath: str, prepend: str = "", append: str = ""):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at {filepath}")

        self.filepath = filepath
        self.prepend = prepend
        self.append = append

    def show(self):
        """
        Displays a download link for the file specified by `self.filepath`.

        Example:
            link = DownloadFileLink("/path/to/file.txt")
            link.show()

        Or better, cache results:
            @st.cache_resource
            def get_file_links(docs: List):
                for doc in docs:
                    link = DownloadFileLink(doc)
                    link.show()

            get_file_link(docs)
        """
        with open(self.filepath, "rb") as f:
            data = f.read()

        encoded_file = base64.b64encode(data).decode()
        filename = os.path.basename(self.filepath)
        href = f'{self.prepend}<a href="data:application/octet-stream;base64,{encoded_file}" download="{filename}">{filename}</a>{self.append}'

        st.markdown(href, unsafe_allow_html=True)
