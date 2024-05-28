import os
from networkx import is_connected
import streamlit as st
import pandas as pd
from typing import Union
from neo4j import GraphDatabase, exceptions
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.components import GraphDatabaseConnection
from modules.auradb import AuraDB
from modules.utils import GraphFileManager, WarningCapture
from modules.extraction import FewShotDataExtractor
from uwv_toolkit.utils import FileExceptionHandler, load_env, azure_llm
from uwv_toolkit.streamlit.components.streamlit_table_component import (
    StreamlitTableComponent,
)

load_env()


# def get_neo4j_auth(key: str = None) -> Union[str, dict, None]:
#     """Returns the right auth credentials for the Neo4J instance"""
#     if is_neo4j_prod():
#         auth = {
#             "uri": os.getenv("PROD_NEO4J_CONNECTION_URI"),
#             "user": os.getenv("PROD_NEO4J_USER"),
#             "password": os.getenv("PROD_NEO4J_PASSWORD"),
#         }
#     else:
#         auth = {
#             "uri": st.session_state.neo4j_url,
#             "user": st.session_state.neo4j_username,
#             "password": st.session_state.neo4j_password,
#         }

#     if key is not None:
#         return auth[key]
#     else:
#         return auth


# def is_neo4j_prod() -> bool:
#     """Returns True if the prod Neo4J instance is selected"""
#     return st.session_state["neo4j_instance"] == "Productie"


# @st.cache_data
# def get_cached_dev_neo4j_auth():
#     if "neo4j_url" not in st.session_state:
#         st.session_state["neo4j_url"] = os.getenv("NEO4J_CONNECTION_URI")
#     if "neo4j_username" not in st.session_state:
#         st.session_state["neo4j_username"] = os.getenv("NEO4J_USER")
#     if "neo4j_password" not in st.session_state:
#         st.session_state["neo4j_password"] = os.getenv("NEO4J_PASSWORD")

#     return (
#         st.session_state.neo4j_url,
#         st.session_state.neo4j_username,
#         st.session_state.neo4j_password,
#     )


# # @st.cache_data
# # def _get_connection():
# #     if not "graph_database_connection" in st.session_state:
# #         return GraphDatabaseConnection(
# #             url=os.getenv("NEO4J_CONNECTION_URI"),
# #             username=os.getenv("NEO4J_USER"),
# #             password=os.getenv("NEO4J_PASSWORD"),
# #             instance=GraphDatabaseConnection.DEVELOPMENT_DB,
# #         )


def get_connection():
    if not "graph_database_connection" in st.session_state:
        st.session_state.graph_database_connection = None
    elif st.session_state.graph_database_connection is not None:
        st.session_state.graph_database_connection.connect()

    if not "neo4j_url" in st.session_state:
        st.session_state.neo4j_url = os.getenv("NEO4J_CONNECTION_URI")
    if not "neo4j_username" in st.session_state:
        st.session_state.neo4j_username = os.getenv("NEO4J_USER")
    if not "neo4j_password" in st.session_state:
        st.session_state.neo4j_password = os.getenv("NEO4J_PASSWORD")

    return st.session_state.graph_database_connection


class GraphManagerPage(BaseUWVGraphPage):

    def _show_main(self):

        st.title(self._config["page_config"]["page_title"])

        st.markdown(
            "Op deze pagina staan de eerder opgeslagen knowledge graphs en kun je een backup opslaan van de huidige Neo4J instantie. Je kunt deze acties uitvoeren op opgeslagen items:"
        )
        st.markdown(
            "* **Verwijderen**: verwijder de opgeslagen graph.\n"
            "* **Toevoegen aan Neo4J**: laad de graph in de verbonden Neo4J instance. De bestaande graph in de Neo4J instance wordt aangevuld met de graph in dit bestand.\n"
            "* **Reset Neo4J**: laad de graph in Neo4J. De opgeslagen graph in Neo4J wordt eerst verwijderd.\n"
        )

        st.markdown("---")

        st.subheader("👉 Neo4J Instance")

        st.markdown(
            """Vul hieronder de gegevens in van de Neo4J database waar de Knowledge Graph in wordt opgeslagen. Deze database moet al bestaan. Vul de gegevens in en klik op 'Connect' om te verbinden. Als de verbinding is gelukt, wordt de status van de database getoond.
            """
        )
        st.markdown(
            "Meer informatie over waar je deze login details vindt lees je [hier](https://aura.support.neo4j.com/hc/en-us/articles/6787460237843-Neo4j-Aura-Database-Authentication-Neo4j-Database-Username-Password). De Neo4J AuraDB URL (Connection URI) vind je [hier](https://console.neo4j.io/)."
        )

        # Initialize file manager
        file_manager = GraphFileManager(username=st.session_state.username)
        graph_db_connection = get_connection()

        st.markdown("#### Verbinden met Neo4J database")
        st.markdown("Selecteer hieronder met welke Neo4J database je wilt verbinden.")

        st.session_state.neo4j_instance = st.radio(
            "Kies de Neo4J database",
            options=[
                GraphDatabaseConnection.DEVELOPMENT_DB,
                GraphDatabaseConnection.PRODUCTION_DB,
            ],
            captions=[
                "Jouw eigen database waar je mee kunt testen. De authenticatie gegevens vul je hieronder in.",
                "De productie omgeving, waar alleen gevalideerde data in staat.",
            ],
            key="neo4j_instance_radio",
            index=(
                graph_db_connection is not None
                and graph_db_connection.is_prod_connection()
            ),
        )

        st.text_input(
            label="Neo4J URL",
            key="neo4j_url",
            help="Neo4J database URL",
            disabled=(
                st.session_state.neo4j_instance == GraphDatabaseConnection.PRODUCTION_DB
            ),
        )
        st.text_input(
            label="Username",
            key="neo4j_username",
            help="Neo4J database username",
            disabled=(
                st.session_state.neo4j_instance == GraphDatabaseConnection.PRODUCTION_DB
            ),
        )
        st.text_input(
            label="Password",
            key="neo4j_password",
            type="password",
            help="Neo4J database password",
            disabled=(
                st.session_state.neo4j_instance == GraphDatabaseConnection.PRODUCTION_DB
            ),
        )

        connect_with_db = st.button(
            label="Save & Connect",
            key="neo4j_connect_button",
            help="Connect to Neo4J database",
        )

        if connect_with_db:
            if (
                st.session_state.neo4j_instance
                == GraphDatabaseConnection.DEVELOPMENT_DB
            ):
                # Connect to the development database
                url = st.session_state.neo4j_url
                username = st.session_state.neo4j_username
                password = st.session_state.neo4j_password
            else:
                # Connect to the development database but don't show the credentials
                url = os.getenv("PROD_NEO4J_CONNECTION_URI")
                username = os.getenv("PROD_NEO4J_USER")
                password = os.getenv("PROD_NEO4J_PASSWORD")

            graph_db_connection = GraphDatabaseConnection(
                url=url,
                username=username,
                password=password,
                instance=st.session_state.neo4j_instance,
            )
            graph_db_connection.connect()

            if graph_db_connection.is_connected():
                st.session_state.graph_database_connection = graph_db_connection
            else:
                st.session_state.graph_database_connection = None

        if graph_db_connection:
            # Yay, we're connected
            graph_db_connection.show()
        else:
            # Not connected yet.
            st.warning("Nog niet verbonden met een Neo4J database.")

        st.markdown("---")

        st.subheader("👉 Maak een backup")
        if graph_db_connection is None or not graph_db_connection.is_connected():
            st.info("Verbind eerst met de Neo4J instance om een backup te maken.")
        else:
            st.markdown("Maak een backup van de huidige Neo4J instantie.")

            description = st.text_area(
                "Opmerking bij de backup", key="backup_description"
            )

            if st.button("Maak backup", key="backup_button"):
                # Placeholder for graph object
                auradb = AuraDB(
                    graph_db_connection.get_url(),
                    graph_db_connection.get_username(),
                    graph_db_connection.get_password(),
                )
                graph = auradb.get_knowledge_graph()

                # Save the graph and get feedback
                result = file_manager.save_graph_file(
                    graph=graph,
                    db_name=st.session_state.neo4j_instance,
                    description=description,
                )
                if result == "Graph opgeslagen.":
                    st.success(result)
                else:
                    st.warning(result)

        st.markdown("---")

        st.subheader("👉 Opgeslagen bestanden")

        # Display and manage saved graphs
        df = file_manager.saved_graphs_df()

        if len(df) == 0:
            st.info("Er zijn geen opgeslagen bestanden.")
        else:
            st.markdown(
                "Uitleg bij de acties:\n"
                "* **Verwijderen**: verwijder het bestand. Let op: het bestand is hierna echt weg. Geen backups!\n"
                "* **Upload**: laad de graph in de Neo4J instance. De bestaande graph in de Neo4J instance wordt aangevuld met de graph in dit bestand.\n"
                "* **Truncate en upload**: laad de graph in Neo4J. De opgeslagen graph in Neo4J wordt eerst verwijderd.\n"
            )
            st.error(
                "**Let op**: Als je op de actie knoppen drukt, wordt deze actie direct uitgevoerd. Je krijgt geen waarschuwingen of bevestigingsstappen!",
                icon="🚨",
            )

            if not graph_db_connection or not graph_db_connection.is_connected():
                st.warning(
                    "Je bent nog niet verbonden met een Neo4J database. Verbind eerst met een Neo4J database om acties uit te voeren."
                )
            else:
                st.info(
                    f"De acties worden uitgevoerd op de **{graph_db_connection.instance()}** Neo4J instance."
                )

            warning_container = st.container()

            def my_action_column_content(
                index, row: pd.Series, column: st.delta_generator.DeltaGenerator
            ):
                if (
                    graph_db_connection is None
                    or not graph_db_connection.is_connected()
                ):
                    # don't show actions if not connected
                    return

                if column.button("Verwijder", key=f"{index}verwijder"):
                    file_manager.delete_graph_file(row["Bestandsnaam"])
                    warning_container.success("File deleted.")
                    st.rerun()

                auradb = AuraDB(
                    uri=graph_db_connection.get_url(),
                    user=graph_db_connection.get_username(),
                    password=graph_db_connection.get_password(),
                )
                if column.button("Toevoegen aan Neo4J", key=f"{index}upload"):
                    graph = file_manager.unpickle_graph(row["Bestandsnaam"])

                    with WarningCapture() as wc:
                        auradb.import_list(graph["nodes"] + graph["relationships"])

                    if len(wc.captured_warnings) == 0:
                        warning_container.success("Graph uploaded successfully.")
                    else:
                        for warn in wc.captured_warnings:
                            warning_container.warning(warn)

                if column.button("Reset Neo4J", key=f"{index}reset"):
                    graph = file_manager.unpickle_graph(row["Bestandsnaam"])
                    auradb.cleanup()
                    with WarningCapture() as wc:
                        auradb.import_list(graph["nodes"] + graph["relationships"])

                    if len(wc.captured_warnings) == 0:
                        warning_container.success("Graph reset successfully.")
                    else:
                        for warn in wc.captured_warnings:
                            warning_container.warning(warn)

            table_component = StreamlitTableComponent(
                df, "Acties", my_action_column_content
            )

            table_component.show()


try:
    p = GraphManagerPage(
        page_config={
            "page_title": "Graph Manager 💿",
            "page_icon": "🏝️",
            "layout": "wide",
        },
    )

    p.show()

except Exception as e:
    FileExceptionHandler.handle(exception=e)
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
