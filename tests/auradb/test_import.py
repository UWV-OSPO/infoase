import os
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_community.graphs.neo4j_graph import Neo4jGraph
from langchain_community.graphs.graph_document import Node, Relationship
from src.modules.utils import WarningCapture
from src.modules.auradb.auradb import AuraDB


@pytest.fixture(name="neo4j_graph")
def fixture_neo4j_graph():
    connection_uri = os.getenv("NEO4J_CONNECTION_URI")
    username = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    return Neo4jGraph(url=connection_uri, username=username, password=password)


@pytest.fixture(name="auradb")
def fixture_auradb():
    uri = os.getenv("NEO4J_CONNECTION_URI")
    auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

    return AuraDB(uri, auth[0], auth[1])


def test_import_list_node(auradb):
    auradb.cleanup()

    with WarningCapture() as wc:
        auradb.import_list(
            [
                Node(
                    id="walter", type="Person", properties={"name": "Walter", "age": 30}
                ),
            ]
        )

    assert len(wc.captured_warnings) == 0


def test_update_node_property(auradb):
    auradb.cleanup()

    with WarningCapture() as wc:
        auradb.import_list(
            [
                Node(id="walter", type="Person", properties={"name": "Walter"}),
            ]
        )

    kg = auradb.get_knowledge_graph()
    assert len(kg["nodes"]) == 1
    assert len(kg["relationships"]) == 0
    assert kg["nodes"][0].properties["name"] == "Walter"
    assert "age" not in kg["nodes"][0].properties
    assert len(wc.captured_warnings) == 0

    with WarningCapture() as wc:
        auradb.import_list(
            [
                Node(id="walter", type="Person", properties={"age": "30"}),
            ]
        )

    kg2 = auradb.get_knowledge_graph()
    assert len(kg2["nodes"]) == 1
    assert len(kg2["relationships"]) == 0
    assert kg2["nodes"][0].properties["name"] == "Walter"
    assert "age" in kg2["nodes"][0].properties
    assert len(wc.captured_warnings) == 0


def test_update_node_label(auradb):
    auradb.cleanup()

    with WarningCapture() as wc:
        auradb.import_list(
            [
                Node(id="walter", type="Person", properties={"name": "Walter"}),
            ]
        )

    kg = auradb.get_knowledge_graph()
    assert len(kg["nodes"]) == 1
    assert len(kg["relationships"]) == 0
    assert kg["nodes"][0].type == "Person"
    assert len(wc.captured_warnings) == 0

    with WarningCapture() as wc:
        auradb.import_list(
            [
                Node(id="walter", type="Employee", properties={"name": "Walter"}),
            ]
        )

    kg2 = auradb.get_knowledge_graph()
    assert len(kg2["nodes"]) == 1
    assert len(kg2["relationships"]) == 0
    assert kg2["nodes"][0].properties["name"] == "Walter"
    assert kg2["nodes"][0].type == "Employee"
    assert len(wc.captured_warnings) == 0


def test_import_list_relationship_warning(neo4j_graph):
    uri = os.getenv("NEO4J_CONNECTION_URI")
    auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

    auradb = AuraDB(uri, auth[0], auth[1])
    auradb.cleanup()

    alice = Node(id="alice", type="Person", properties={"name": "Alice"})
    bob = Node(id="bob", type="Person", properties={"name": "Bob"})

    # This goes wrong because alice and bob are not in the database yet.
    with WarningCapture() as wc:
        auradb.import_list(
            [
                Relationship(type="knows", source=alice, target=bob, properties={}),
            ]
        )

    # Display captured warnings
    # for warn in wc.captured_warnings:
    #     print(warn)

    assert len(wc.captured_warnings) == 1
    assert "Cannot create relationship" in wc.captured_warnings[0]


def test_import_list_relationship(neo4j_graph):
    uri = os.getenv("NEO4J_CONNECTION_URI")
    auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

    auradb = AuraDB(uri, auth[0], auth[1])
    auradb.cleanup()

    alice = Node(id="alice", type="Person", properties={"name": "Alice"})
    bob = Node(
        id="bob", type="Person", properties={"name": "Bob", "occupation": "developer"}
    )

    with WarningCapture() as wc:
        auradb.import_list(
            [
                alice,
                bob,
                Relationship(type="knows", source=alice, target=bob),
            ]
        )

    assert len(wc.captured_warnings) == 0
