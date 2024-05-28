import pytest
import os
import shutil
from langchain_community.graphs import Neo4jGraph
from langchain_community.graphs.graph_document import Node, Relationship
from langchain.chains import GraphCypherQAChain
from modules.utils import Utilities
from modules.utils.graph_file_manager import GraphFileManager
from modules.auradb import AuraDB
from modules.utils.load_env import load_env

load_env()


@pytest.fixture(autouse=True)
def print_start(request):
    """Show the test name before running it"""
    print(
        "\033[01m \033[96m {}\033[00m".format(
            "\n\n🧪🧪 TEST("
            + request.module.__name__
            + "."
            + request.node.name
            + ") 🧪🧪"
        )
    )


@pytest.fixture(name="neo4j_graph")
def fixture_neo4j_graph():
    connection_uri = os.getenv("NEO4J_CONNECTION_URI")
    username = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    return Neo4jGraph(url=connection_uri, username=username, password=password)


@pytest.fixture(name="auradb")
def fixture_auradb():
    return AuraDB(
        os.getenv("NEO4J_CONNECTION_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD"),
    )


@pytest.fixture(name="cypher_chain")
def fixture_cypher_chain(neo4j_graph):

    llm = Utilities.create_llm("azure", temperature=0)
    return GraphCypherQAChain.from_llm(
        llm, graph=neo4j_graph, verbose=os.getenv("VERBOSE") == "1"
    )


@pytest.fixture(name="walterbob_graph")
def fixture_auradb_graph_walterbob(auradb):

    walter = Node(
        id="walter",
        type="Person",
        properties={"name": "Walter", "age": 30, "location": "Delft"},
    )
    bob = Node(
        id="bob",
        type="Person",
        properties={"name": "Bob", "age": 35, "location": "Amsterdam"},
    )

    auradb.cleanup()
    auradb.import_list(
        [
            walter,
            bob,
            Relationship(
                source=walter, type="KNOWS", target=bob, properties={"since": 2019}
            ),
        ]
    )
    return auradb


@pytest.fixture(name="waltdisney_graph")
def fixture_auradb_graph_walt_disney(auradb):
    mgr = GraphFileManager(username="michiel.buisman", directory="data/")

    # Copy the file to the destination directory
    shutil.copy(
        "tests/langchain/data/walt_disney_graph.pkl",
        "./tmp/test/data",
    )

    # Unpickle the graph
    graph = mgr.unpickle_graph("walt_disney_graph.pkl")

    # Clean up the database and import the graph
    auradb.cleanup()
    auradb.import_list(graph["nodes"] + graph["relationships"])

    return auradb
