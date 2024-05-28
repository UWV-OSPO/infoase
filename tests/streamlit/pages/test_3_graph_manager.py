import os
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_community.graphs.graph_document import Node, Relationship
from tests.base_pytest import start_authenticated_app_test
from streamlit.testing.v1 import AppTest
from modules.utils.load_env import load_env
from modules.auradb import AuraDB

load_env()


@pytest.fixture(name="at")
def fixture_at() -> AppTest:
    # Remove all files from ./tmp/test/data/saved_graphs
    os.system("rm -rf ./tmp/test/data/saved_graphs/*")
    return start_authenticated_app_test("./src/pages/3_Graph manager.py")


@pytest.fixture(name="auradb")
def fixture_auradb():
    auradb = AuraDB(
        os.getenv("NEO4J_CONNECTION_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD"),
    )
    auradb.cleanup()

    alice = Node(id="alice", type="Person", properties={"name": "Alice"})
    bob = Node(
        id="bob", type="Person", properties={"name": "Bob", "occupation": "developer"}
    )
    auradb.import_list(
        [
            alice,
            bob,
            Relationship(type="knows", source=alice, target=bob),
        ]
    )
    return auradb


@pytest.fixture(name="at_with_db")
def fixture_at_with_db(at) -> AppTest:
    at.radio("neo4j_instance_radio").set_value("Ontwikkeling")
    at.text_input(key="neo4j_url").set_value(os.getenv("NEO4J_CONNECTION_URI"))
    at.text_input(key="neo4j_username").set_value(os.getenv("NEO4J_USER"))
    at.text_input(key="neo4j_password").set_value(os.getenv("NEO4J_PASSWORD"))

    at.button("neo4j_connect_button").click().run()
    return at


def test_load_page(at: AppTest):
    at.run()
    assert not at.exception


def test_neo4j_config_error(at: AppTest):
    """
    Checks whether or not the neo4j connection is successful when incorrect
    credentials are provided.
    """
    assert at.session_state.graph_database_connection is None
    # assert at.session_state.neo4j_connected is False

    at.radio("neo4j_instance_radio").set_value("Ontwikkeling")
    at.text_input("neo4j_url").set_value("neo4j://localhost:7687")
    at.button("neo4j_connect_button").click().run(timeout=600)

    assert len(at.error) > 0
    assert any("Connection to Neo4J failed" in error.body for error in at.error)
    assert all("Connection to Neo4J established." not in msg.body for msg in at.success)


def test_neo4j_config_success(at_with_db: AppTest):
    """
    Checks whether or not the neo4j connection is successful when the correct
    credentials are provided.
    """

    assert all("Connection to Neo4J failed" not in msg.body for msg in at_with_db.error)
    assert any(
        "Verbonden met Neo4J (Ontwikkeling)." in msg.body for msg in at_with_db.success
    )


def test_backup(at_with_db: AppTest):
    """
    Checks whether or not the backup is successful when the correct
    credentials are provided.
    """

    at = at_with_db
    at.text_area("backup_description").set_value("test backup")
    at.button("backup_button").click().run(timeout=600)

    assert any("Graph opgeslagen." in msg.body for msg in at.success)


def test_remove_backup(at_with_db: AppTest):
    """
    Checks whether or not the backup is successful when the correct
    credentials are provided.
    """

    at = at_with_db
    at.text_area("backup_description").set_value("test backup")
    at.button("backup_button").click().run()

    assert any("Graph opgeslagen." in msg.body for msg in at.success)
    assert not any("File deleted." in msg.body for msg in at.success)
    at.button("0verwijder").click().run()

    assert any("File deleted." in msg.body for msg in at.success) or any(
        "Er zijn geen opgeslagen bestanden." in msg.body for msg in at.info
    )


def test_upload_backup(at_with_db: AppTest):
    """
    Checks whether or not the backup is successful when the correct
    credentials are provided.
    """

    at = at_with_db
    at.text_area("backup_description").set_value("test backup")
    at.button("backup_button").click().run()

    assert any("Graph opgeslagen." in msg.body for msg in at.success)
    assert not any("File deleted." in msg.body for msg in at.success)
    at.button("0upload").click().run()

    assert any("Graph uploaded successfully." in msg.body for msg in at.success)


def test_reset_upload_backup(at_with_db: AppTest, auradb: AuraDB):
    """
    Checks whether or not the backup is successful when the correct
    credentials are provided.
    """

    at = at_with_db

    # Save the current graph, without Roy.
    at.text_area("backup_description").set_value("test backup")
    at.button("backup_button").click().run()
    assert any("Graph opgeslagen." in msg.body for msg in at.success)

    # Insert Roy to the graph
    auradb.import_list(
        [
            Node(id="roy", type="Person", properties={"name": "Roy"}),
        ]
    )
    graph = auradb.get_knowledge_graph()
    assert any(node.id == "roy" for node in graph["nodes"])

    # # Reset the graph, removing Roy
    at.button("0reset").click().run()
    assert any("Graph reset successfully." in msg.body for msg in at.success)

    # Check if Roy is removed
    graph = auradb.get_knowledge_graph()
    assert not any(node.id == "roy" for node in graph["nodes"])
