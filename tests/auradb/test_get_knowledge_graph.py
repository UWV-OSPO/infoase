import os
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from neo4j import GraphDatabase
from src.modules.auradb.auradb import AuraDB
from langchain_community.graphs.graph_document import Node, Relationship


@pytest.fixture(name="auradb")
def fixture_auradb():
    uri = os.getenv("NEO4J_CONNECTION_URI")
    auth = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

    return AuraDB(uri, auth[0], auth[1])


def test_get_knowledge_graph(auradb):
    auradb.cleanup()

    alice = Node(id="alice", type="Person", properties={"name": "Alice"})
    bob = Node(id="bob", type="Person", properties={"name": "Bob"})
    auradb.import_list(
        [
            alice,
            bob,
            Relationship(type="knows", source=alice, target=bob, properties={}),
        ]
    )

    kg = auradb.get_knowledge_graph()

    assert len(kg["nodes"]) == 2
    assert len(kg["relationships"]) == 1
    assert all(isinstance(node, Node) for node in kg["nodes"])
    assert all(
        isinstance(relationship, Relationship) for relationship in kg["relationships"]
    )


def test_get_knowledge_graph_empty(auradb):
    auradb.cleanup()

    kg = auradb.get_knowledge_graph()

    assert len(kg["nodes"]) == 0
    assert len(kg["relationships"]) == 0
