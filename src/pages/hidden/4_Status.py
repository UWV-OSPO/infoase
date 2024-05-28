import os
import streamlit as st

from neo4j import GraphDatabase, exceptions
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.utils import FileExceptionHandler


class StatusPage(BaseUWVGraphPage):
    def _page_main(self):
        st.markdown(
            "Deze pagina krijgt later de functie om de status weer te geven van de Knowledge Graph Server (Neo4J AuraDB)."
        )

        URI = os.getenv("NEO4J_CONNECTION_URI")
        AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

        try:
            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                driver.verify_connectivity()

            st.success("🟢 Connection to Neo4j established.")
        except exceptions.ServiceUnavailable:
            st.error(
                "🔴 Connection to Neo4j failed.  "
                "Please ensure that the url is correct."
            )
        except exceptions.AuthError:
            st.error(
                "🔴 Connection to Neo4j failed. "
                "Please ensure that the username and password are correct."
            )

        except Exception as e:
            st.error(f"🔴 Connection to Neo4j failed: {e}")


try:
    p = StatusPage(page_title="Server status page")
    p.show()
except Exception as e:
    FileExceptionHandler.handle(exception=e)

    # Display an error message and stop rendering.
    print(e)
    st.error("Er is een fout opgetreden. Contacteer de ontwikkelaars.")
