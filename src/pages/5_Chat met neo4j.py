import os
import sys
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from neo4j.exceptions import ClientError, DriverError
from uwv_toolkit.streamlit.page.mixins import ChatMixin
from uwv_toolkit.db.feedback import FeedbackModel
from uwv_toolkit.utils import azure_llm, FileExceptionHandler, load_env
from modules.streamlit.components import GraphDatabaseConnection
from modules.smz import SmzGraphQAChain as Chain
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.graph_chart import GraphChart
from modules.streamlit.utils import is_admin
from modules.auradb.auradb import AuraDB

load_env()


@st.cache_data
def cache_custom_settings():

    if "custom_neo4j_url" in st.session_state:
        url = st.session_state.custom_neo4j_url
    else:
        url = os.environ.get("NEO4J_CONNECTION_URI")
    if "custom_neo4j_username" in st.session_state:
        username = st.session_state.custom_neo4j_username
    else:
        username = os.environ.get("NEO4J_USER")
    if "custom_neo4j_password" in st.session_state:
        password = st.session_state.custom_neo4j_password
    else:
        password = os.environ.get("NEO4J_PASSWORD")

    return url, username, password


def get_custom_auth_settings():
    # als session niet leeg, return sessie
    # als leeg, dan return cache
    if (
        "custom_neo4j_url" in st.session_state
        and "custom_neo4j_username" in st.session_state
        and "custom_neo4j_password" in st.session_state
    ):
        return (
            st.session_state.custom_neo4j_url,
            st.session_state.custom_neo4j_username,
            st.session_state.custom_neo4j_password,
        )
    return cache_custom_settings()


def get_custom_connection_component():
    if "custom_graph_db_connection" in st.session_state:
        return st.session_state.custom_graph_db_connection

    url, username, password = get_custom_auth_settings()

    if url == "" or username == "" or password == "":
        return None

    if url == os.environ.get("PROD_NEO4J_CONNECTION_URI"):
        instance_name = GraphDatabaseConnection.PRODUCTION_DB
    else:
        instance_name = GraphDatabaseConnection.DEVELOPMENT_DB

    st.session_state.custom_graph_db_connection = GraphDatabaseConnection(
        url=url,
        username=username,
        password=password,
        instance=instance_name,
        show_messages=True,
    )
    return st.session_state.custom_graph_db_connection


class Neo4JProdChatPage(ChatMixin, BaseUWVGraphPage):

    def _display_sources_expander(
        self, container: DeltaGenerator, sources: list
    ) -> None:
        """
        Method to display sources in an expander.

        Args:
            chat_message_block: the chat message block
            sources: list of sources

        Returns:
            None
        """
        messages = self._get_chat_session_state("messages")

        if (
            container is not None
            and sources is not None
            and self._config["chat"]["enable_source"]
            and len(messages) > 1
            and messages[-1]["role"] == "assistant"
        ):
            with container:
                with st.expander("🔗 Bekijk bronnen:"):
                    st.write(sources)

    def _show_reset_button(self):
        chat_namespace = self._config["chat"]["chat_history_namespace"]
        if (
            chat_namespace in st.session_state
            and len(self._get_chat_session_state("chat_history")) > 1
            and st.button("Begin een lege chat", key="clear_chat")
        ):
            self._set_chat_session_state("chat_history", [])
            self._set_chat_session_state("messages", [])

    def _show_graph_chart(self, graph_db_connection):
        db = AuraDB(
            uri=graph_db_connection.get_url(),
            user=graph_db_connection.get_username(),
            password=graph_db_connection.get_password(),
        )

        graph_content = db.get_knowledge_graph()
        if len(graph_content["nodes"]) > 0:
            chart = GraphChart(
                nodes=graph_content["nodes"], edges=graph_content["relationships"]
            )
            with st.expander("Inspecteer graph", expanded=False):
                st.info(
                    "Op de nodes en relaties klikken wordt niet ondersteund en geeft een foutmelding."
                )
                chart.show(add_container=False)

        else:
            st.write("Er zijn geen nodes om weer te geven, de database is leeg.")

    def _show_main(self):

        if not is_admin(self._admin_users):
            st.error("Je hebt geen toegang tot deze pagina.")
            return

        st.title(self._config["page_config"]["page_title"])
        st.markdown(
            "Op deze pagina is het mogelijk om te chatten met een Neo4J database."
        )

        # Init settings from cache.
        (
            st.session_state.custom_neo4j_url,
            st.session_state.custom_neo4j_username,
            st.session_state.custom_neo4j_password,
        ) = get_custom_auth_settings()

        with st.expander(
            "Neo4J verbinding instellingen",
            expanded=(st.session_state.custom_neo4j_url == ""),
        ):
            with st.form("custom_graph_db_connection_settings"):
                st.text_input(
                    label="Neo4J URL",
                    key="custom_neo4j_url",
                    help="Neo4J database URL",
                    placeholder="for example, bolt+ssc://8f78fa35.databases.neo4j.io",
                )
                st.text_input(
                    label="Username",
                    key="custom_neo4j_username",
                    placeholder="for example, neo4j",
                    help="Neo4J database username",
                )
                st.text_input(
                    label="Password",
                    key="custom_neo4j_password",
                    type="password",
                    help="Neo4J database password",
                )

                # Every form must have a submit button.
                submitted = st.form_submit_button("Submit")
                if submitted:

                    # Refresh the cache
                    cache_custom_settings.clear()
                    cache_custom_settings()
                    if "custom_graph_db_connection" in st.session_state:
                        del st.session_state.custom_graph_db_connection

        graph_db_connection = get_custom_connection_component()

        if graph_db_connection:
            connected = graph_db_connection.show()
            if connected:

                graph = graph_db_connection.get_neo4j_graph()

                self._show_graph_chart(graph_db_connection)
                self._show_reset_button()

                self.display_history()

                if user_query := st.chat_input("Stel een vraag over een document..."):
                    self.display_msg(user_query, "user")

                    with st.spinner("Aan het nadenken..."):
                        chain = Chain(llm=azure_llm(temperature=0.1), graph=graph)
                        result = chain.ask(
                            question=user_query,
                            # The user query was already added to the chat history.
                            chat_history=self._get_chat_session_state("chat_history")[
                                :-1
                            ],
                        )

                    self.display_msg(result, "assistant")
        else:
            st.warning("Vul de Neo4J verbinding instellingen in en klik op 'Submit'.")


try:

    page = Neo4JProdChatPage(
        page_config={
            "page_title": "Infoase Neo4J Chat (Ontwikkel) 🤖",
            "page_icon": "🤖",
            "layout": "wide",
        },
        chat={
            "enable_source": True,
            "enable_feedback": True,
            "chat_history_namespace": "neo4j_custom_chat_history",
            "feedback_model": FeedbackModel,
            "chat_type": "Neo4J Ontwikkel",
        },
    )
    page.show()

except ClientError as e:
    FileExceptionHandler.handle(exception=e, extra_info=str(st.session_state))
    # Display an error message and stop rendering.
    st.error(
        f"Bij het zoeken naar relevante informatie over je vraag (in Neo4J) is een fout opgetreden:\n\n{e}\n\nProbeer het nog eens."
    )
except ValueError as e:
    FileExceptionHandler.handle(exception=e, extra_info=str(st.session_state))
    # Display an error message and stop rendering.

    if "Could not connect to Neo4j database." in str(e):
        st.error(
            "Er is een verbingsfout met Neo4J. "
            "Ga naar de Graph manager en maakt opnieuw verbinding."
        )
    else:
        st.error(
            f"Bij het zoeken naar relevante informatie over je vraag (in Neo4J) is een fout opgetreden:\n\n{e}\n\Ververs de pagina en probeer het nog eens."
        )
except DriverError as e:
    FileExceptionHandler.handle(exception=e, extra_info=str(st.session_state))
    # Display an error message and stop rendering.
    st.error(
        "Er is een verbingsfout met Neo4J. Ga naar de Graph manager en maakt verbinding."
    )
except Exception as e:
    FileExceptionHandler.handle(exception=e, extra_info=str(st.session_state))
    # Display an error message and stop rendering.
    st.error("An error occurred. Please contact the developer.")
