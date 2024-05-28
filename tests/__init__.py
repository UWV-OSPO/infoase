import sys
import os
import warnings
import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
from src.modules.utils.load_env import load_env
from langchain.globals import set_verbose
from langchain_community.graphs import Neo4jGraph

load_env()

set_verbose((os.getenv("VERBOSE") == "1"))


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture(name="neo4j_graph")
def fixture_neo4j_graph():
    connection_uri = os.getenv("NEO4J_CONNECTION_URI")
    username = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    return Neo4jGraph(url=connection_uri, username=username, password=password)
