import streamlit as st

from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase, exceptions
from modules.streamlit.components import BaseStreamlitComponent
from uwv_toolkit.utils import load_env


class GraphDatabaseConnection(BaseStreamlitComponent):

    _url: str
    _username: str
    _password: str
    _instance: str
    _connected: bool = False
    _neo4j_graph: Neo4jGraph = None

    DEVELOPMENT_DB = "Ontwikkeling"
    PRODUCTION_DB = "Productie"

    def __init__(
        self,
        url: str = None,
        username: str = None,
        password: str = None,
        instance: str = None,
        show_messages: bool = True,
    ):
        load_env()

        if not instance in (self.DEVELOPMENT_DB, self.PRODUCTION_DB):
            raise ValueError(
                "The connected instance should be either 'Ontwikkeling' or 'Productie'."
            )

        self._url = url
        self._username = username
        self._password = password
        self._instance = instance
        self._show_messages = show_messages

    def is_connected(self) -> bool:
        """
        Check if the connection is established.

        Returns:
            bool: True if the connection is established, False otherwise.
        """
        return self._connected

    def instance(self) -> str:
        """
        Get the connected instance.

        Returns:
            str: The connected instance.
        """
        return self._instance

    def get_neo4j_graph(self) -> Neo4jGraph:
        """
        Get the Neo4jGraph instance.

        Returns:
            Neo4jGraph: The Neo4jGraph instance.
        """
        return self._neo4j_graph

    def is_dev_connection(self) -> bool:
        """
        Check if the connection is established with the development database.

        Returns:
            bool: True if the connection is established, False otherwise.
        """
        return self._instance == self.DEVELOPMENT_DB

    def is_prod_connection(self) -> bool:
        """
        Check if the connection is established with the production database.

        Returns:
            bool: True if the connection is established, False otherwise.
        """
        return self._instance == self.PRODUCTION_DB

    def get_url(self) -> str:
        """
        Get the URL of the graph database.

        Returns:
            str: The URL of the graph database.
        """
        return self._url

    def get_username(self) -> str:
        """
        Get the username of the graph database.

        Returns:
            str: The username of the graph database.
        """
        return self._username

    def get_password(self) -> str:
        """
        Get the password of the graph database.

        Returns:
            str: The password of the graph database.
        """
        return self._password

    # def connection(self) -> dict:

    def connect(self) -> bool:
        """
        Connect to the graph database.

        Returns:
            bool: True if the connection is established, False otherwise.
        """
        try:

            self._neo4j_graph = Neo4jGraph(
                url=self._url, username=self._username, password=self._password
            )

            self._connected = True

            return {
                "connected": True,
                "message": f"🟢 Verbonden met Neo4J ({self._instance}).",
            }
        except exceptions.ServiceUnavailable:
            message = (
                "Connection to Neo4J failed. Please ensure that the url is correct."
            )
        except exceptions.AuthError:
            message = "Connection to Neo4J failed. Please ensure that the username and password are correct."
        except Exception as e:
            print(e)
            message = f"Connection to Neo4J failed: {e}"

        self._connected = False
        return {
            "connected": False,
            "message": f"🔴 Fout bij het verbinden met Neo4J ({self._instance}): {message}",
        }

    def get_auth(self) -> dict:
        """
        Get the authentication details.

        Returns:
            dict: The authentication details.
        """
        return {
            "url": self._url,
            "username": self._username,
            "password": self._password,
        }

    def show(self):
        """
        Renders the connection component.

        Returns:
            bool: True if the connection is established, False otherwise.
        """

        connection_result = self.connect()

        if self._show_messages:
            if connection_result["connected"]:
                st.success(connection_result["message"])
            else:
                st.error(connection_result["message"])

            if "8f78fa35.databases.neo4j.io" in self._url:
                st.warning(
                    "**Let op:** deze Neo4J database wordt ook gebruikt voor andere test doeleinden.De database wordt vaak geleegd. Maak een eigen Neo4J database aan en vul de login details hieronder in."
                )

        return self._connected
