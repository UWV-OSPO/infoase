import os
import tempfile
import time
import streamlit as st
from langchain_community.document_loaders import (
    UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
)
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.utils import GraphFileManager
from modules.extraction import FewShotDataExtractor, extraction_prompt, system_prompt
from uwv_toolkit.utils import FileExceptionHandler, load_env, azure_llm

load_env()


class DocToKgPage(BaseUWVGraphPage):

    def _process_file(self, filepath: str):

        if filepath.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filepath.endswith(".docx"):
            loader = UnstructuredWordDocumentLoader(filepath)
        elif filepath.endswith(".html") or filepath.endswith(".htm"):
            loader = UnstructuredHTMLLoader(filepath)
        else:
            st.error(f"Bestandstype niet ondersteund: {filepath.split('.')[-1]}.")
            return

        data = loader.load()

        llm = azure_llm(temperature=st.session_state.temperature)
        extractor = FewShotDataExtractor(
            llm,
            system_prompt=st.session_state.prompt,
            verbose=(os.getenv("VERBOSE") == "1"),
        )

        try:
            graph = extractor.run_list(data)
        except Exception as e:
            st.error(
                f"Er is een fout opgetreden tijdens de extractie. Probeer het nogmaals. \n\n{e}"
            )

        return graph

    def _show_main(self):

        st.title(self._config["page_config"]["page_title"])
        if "graph" not in st.session_state:
            st.session_state.graph = None

        st.markdown(
            "Op deze pagina kun je documenten om laten zetten naar een Knowledge Graph."
        )

        st.markdown("---")

        file_to_process = st.radio(
            "Kies een document om te verwerken",
            options=[
                "82158.html",
                "82159.html",
                "kickoff.docx",
                "test.pdf",
                "Upload een nieuw document",
            ],
            captions=[
                "Wetsuitleg WIA, WAO/WAZ/oWajong en ZW &rsaquo; Wettelijk kader beoordeling re-integratie-inspanningen",
                "Wetsuitleg WIA, WAO/WAZ/oWajong en ZW &rsaquo; Professioneel kader beoordeling re-integratie-inspanningen",
                "Infoase kick-off - voorbereidende tekst voor de sessie op 15 februari 2024",
                "Test document",
                "Bestandstypes pdf, docx, html zijn ondersteund.",
            ],
            index=0,
        )

        uploaded_file = st.file_uploader(
            "Upload een document", type=["pdf", "docx", "html"]
        )

        with st.expander("✍️ Pas prompt aan", expanded=False):
            st.slider("LLM Temperature", 0.0, 1.0, 0.0, key="temperature")

            st.text_area(
                "System prompt",
                value=system_prompt,
                height=300,
                key="prompt",
            )
            st.warning(
                "Sla je prompt en temperatuur instellingen op, dit wordt nergens opgeslagen."
            )

        if st.button("Start extractie", key="start_extraction"):

            if file_to_process == "Upload een nieuw document":
                if uploaded_file is None:
                    st.warning("Upload een document om te verwerken.")
                    return
                else:

                    file_extension = uploaded_file.name.split(".")[-1]

                    # Save uploaded file to tmp
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=("." + file_extension)
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file.seek(0)
                        tmp_file.close()
                        filepath = tmp_file.name
            elif file_to_process == "82158.html":
                filepath = "data/proef-infoase-jan2024/82158.html"
            elif file_to_process == "82159.html":
                filepath = "data/proef-infoase-jan2024/82158.html"
            elif file_to_process == "kickoff.docx":
                filepath = "data/proef-infoase-jan2024/Infoase - voorbereidende tekst voor de sessie op 15 februari 2024.docx"
            elif file_to_process == "test.pdf":
                filepath = "data/test/disney_test_2p.pdf"
            else:
                raise ValueError("Invalid file selected.")

            with st.spinner(
                "☕️ Bezig met extractie van nodes, relaties en eigenschappen..."
            ):
                st.session_state.graph = self._process_file(filepath)

        if st.session_state.graph:
            graph = st.session_state.graph
            self.show_knowledge_graph(graph)
            st.markdown(
                "Maak een backup van de bovenstaande graph. De backup vind je terug in de [Graph Manager](/Graph_manager). Zet de graph vanuit de Graph Manager over naar Neo4J."
            )

            description = st.text_area(
                "Opmerking bij de backup", key="backup_description"
            )
            if st.button("Maak backup", key="backup_button"):
                nodes = []
                relationships = []

                for graph_doc in graph:
                    nodes += graph_doc.nodes
                    relationships += graph_doc.relationships

                file_manager = GraphFileManager(username=st.session_state.username)
                result = file_manager.save_graph_file(
                    graph={"nodes": nodes, "relationships": relationships},
                    db_name="Extractie",
                    description=description,
                )

                if result == "Graph opgeslagen.":
                    st.success("Graph succesvol opgeslagen, zie graph manager")
                else:
                    st.warning(result)

                time.sleep(5)


try:
    p = DocToKgPage(
        page_config={
            "page_title": "Doc naar Knowledge Graph 📕",
            "page_icon": "🏝️",
            "layout": "wide",
        },
    )

    p.show()

except Exception as e:
    FileExceptionHandler.handle(exception=e)
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
