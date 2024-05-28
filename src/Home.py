import streamlit as st
from uwv_toolkit.utils import FileExceptionHandler
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage


class HomePage(BaseUWVGraphPage):

    def _show_main(self):
        # Description
        st.markdown(
            """
            <h5 style='text-align:center;'>Dit is de hoofdpagina voor de proof-of-technology voor het chatten met documenten ondersteund door Knowledge Graph technologie.</h5>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Pages
        st.subheader("👉 Pagina's")
        st.write(
            """
        - **Tekst naar KG**: Pagina om te experimenteren met het omzetten van kleine hoeveelheden tekst naar een Knowledge Graph.
        - **Document naar KG**: pagina waar we documenten inladen, omzetten naar een knowledge graph en opslaan om via de Graph Manager te importeren in Neo4J.
        - **Graph Manager**: pagina om opgeslagen Knowledge Graphs te beheren en te importeren in Neo4J.
        - **Chat met docs**: chatbot die antwoorden geeft op basis van informatie uit de documenten.
        - **Chat met neo4j**: chatbot die antwoorden geeft op basis van de Knowledge Graph die is opgebouwd door domeinexperts.
        """
        )


try:
    p = HomePage(
        page_config={
            "page_title": "Infoase - 🏝️",
            "page_icon": "🏝️",
            "initial_sidebar_state": "expanded",
        },
    )

    p.show()

except Exception as e:
    FileExceptionHandler.handle(exception=e)
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
