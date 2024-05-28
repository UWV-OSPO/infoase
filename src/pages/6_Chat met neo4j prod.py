import os
import streamlit as st

from streamlit.delta_generator import DeltaGenerator
from neo4j.exceptions import ClientError, DriverError
from langchain_community.graphs import Neo4jGraph
from uwv_toolkit.streamlit.page.mixins import ChatMixin
from uwv_toolkit.db.feedback import FeedbackModel
from uwv_toolkit.utils import azure_llm, FileExceptionHandler, load_env
from modules.streamlit.components import GraphDatabaseConnection
from modules.smz import SmzGraphQAChain as Chain
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.graph_chart import GraphChart
from modules.auradb.auradb import AuraDB

load_env()


def get_prod_connection_component():
    if "prod_graph_db_connection" in st.session_state:
        return st.session_state.prod_graph_db_connection

    # @st.cache_resource
    # def _get_prod_connection_component():
    #     return GraphDatabaseConnection(
    #         url=os.getenv("PROD_NEO4J_CONNECTION_URI"),
    #         username=os.getenv("PROD_NEO4J_USER"),
    #         password=os.getenv("PROD_NEO4J_PASSWORD"),
    #         instance=GraphDatabaseConnection.PRODUCTION_DB,
    #         show_messages=True,
    #     )

    st.session_state.prod_graph_db_connection = GraphDatabaseConnection(
        url=os.getenv("PROD_NEO4J_CONNECTION_URI"),
        username=os.getenv("PROD_NEO4J_USER"),
        password=os.getenv("PROD_NEO4J_PASSWORD"),
        instance=GraphDatabaseConnection.PRODUCTION_DB,
        show_messages=True,
    )
    return st.session_state.prod_graph_db_connection


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

    def _connect_with_graph(self):

        graph_db_connection = get_prod_connection_component()
        graph_db_connection.show()
        if graph_db_connection.is_connected():
            return True

        return False

    def _show_reset_button(self):
        chat_namespace = self._config["chat"]["chat_history_namespace"]
        if (
            chat_namespace in st.session_state
            and len(self._get_chat_session_state("chat_history")) > 1
            and st.button("Begin een lege chat", key="clear_chat")
        ):
            self._set_chat_session_state("chat_history", [])
            self._set_chat_session_state("messages", [])
            # st.session_state[chat_namespace]["chat_history"] = []
            # st.session_state[chat_namespace]["messages"] = []

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
        st.title(self._config["page_config"]["page_title"])
        st.markdown(
            "Op deze pagina is het mogelijk om te chatten met een Neo4J database."
        )

        # Show the status of the connection.
        graph_db_connection = get_prod_connection_component()
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
                        chat_history=self._get_chat_session_state("chat_history")[:-1],
                    )

                self.display_msg(result, "assistant")


try:

    page = Neo4JProdChatPage(
        page_config={
            "page_title": "Infoase Neo4J Chat (Productie) 🤖",
            "page_icon": "🤖",
            "layout": "wide",
        },
        chat={
            "enable_source": True,
            "enable_feedback": True,
            "chat_history_namespace": "neo4j_prod_chat_history",
            "feedback_model": FeedbackModel,
            "chat_type": "Neo4J Productie",
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
