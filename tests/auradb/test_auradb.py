# pylint: disable=E1129
import os
import random
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from neo4j import GraphDatabase
from langchain_community.graphs.graph_document import Node, Relationship
from src.modules.auradb.auradb import AuraDB


@pytest.fixture(name="auradb")
def fixture_auradb():
    return AuraDB(
        os.getenv("NEO4J_CONNECTION_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD"),
    )


def test_auradb_check_status(auradb):
    # Test your auradb instance here
    try:
        auradb.check_status()
    except Exception as e:
        assert False, f"Exception occurred: {str(e)}"


def test_auradb_cleanup(auradb):
    """Clean up test data

    Also see:
    https://aura.support.neo4j.com/hc/en-us/articles/360059882854-Using-APOC-periodic-iterate-to-delete-large-numbers-of-nodes
    """
    auradb.cleanup()
    auradb.import_list(
        [
            Node(id="walter", type="Person", properties={"name": "Walter", "age": 30}),
        ]
    )
    # Check if the node is created
    export = auradb.get_knowledge_graph()
    assert len(export["nodes"]) > 0, "Exported node count is not 0"
    assert len(export["relationships"]) == 0, "Exported node count is not 0"

    auradb.cleanup()

    # Check if the node is still there
    export = auradb.get_knowledge_graph()
    assert len(export["nodes"]) == 0, "Exported node count is not 0"
    assert len(export["relationships"]) == 0, "Exported relationship count is not 0"


def test_auradb_export_json(auradb):
    """Test the export_json() method"""

    # Generate a random filename and check if the file exists in the tmp/ folder.
    # If it exists, delete it.
    filename = f"tmp/export_test_{random.randint(1, 1000000)}.jsonl"
    auradb.export_jsonl(filename=filename)

    assert os.path.exists(filename), f"File {filename} does not exist"

    # Delete the file
    os.remove(filename)


def test_auradb_cleanup(auradb):
    """Clean up test data

    Also see:
    https://aura.support.neo4j.com/hc/en-us/articles/360059882854-Using-APOC-periodic-iterate-to-delete-large-numbers-of-nodes
    """
    auradb.cleanup()
    auradb.import_list(
        [
            Node(id="walter", type="Person", properties={"name": "Walter", "age": 30}),
        ]
    )
    # Check if the node is created
    export = auradb.get_knowledge_graph()
    assert len(export["nodes"]) > 0, "Exported node count is not 0"
    assert len(export["relationships"]) == 0, "Exported node count is not 0"

    auradb.cleanup()

    # Check if the node is still there
    export = auradb.get_knowledge_graph()
    assert len(export["nodes"]) == 0, "Exported node count is not 0"
    assert len(export["relationships"]) == 0, "Exported relationship count is not 0"
