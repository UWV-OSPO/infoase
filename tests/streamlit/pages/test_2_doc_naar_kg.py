import os
import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from streamlit.testing.v1 import AppTest
from tests.base_pytest import start_authenticated_app_test, enable_caching

enable_caching()
PAGE = "./src/pages/2_Document naar KG.py"


def setup_state(at):
    at.session_state.neo4j_connected = True
    at.session_state.neo4j_instance = "Ontwikkeling"
    at.session_state.neo4j_url = os.getenv("NEO4J_CONNECTION_URI")
    at.session_state.neo4j_username = os.getenv("NEO4J_USER")
    at.session_state.neo4j_password = os.getenv("NEO4J_PASSWORD")
    at.run()


def test_load_page():
    at = start_authenticated_app_test(PAGE)
    assert not at.exception


def test_extract_test_doc():
    at = start_authenticated_app_test(PAGE)

    at.radio[0].set_value("test.pdf").run()
    at.button("start_extraction").click().run(timeout=600)
    assert not at.exception
    assert not at.error


def test_extract_and_save_doc():
    at = start_authenticated_app_test(PAGE)
    setup_state(at)

    at.radio[0].set_value("test.pdf").run()
    at.button("start_extraction").click().run(timeout=600)

    assert not at.exception
    assert not at.error

    assert at.button("backup_button")

    at.text_area("backup_description").set_value("test backup").run()
    at.button("backup_button").click().run(timeout=600)

    assert not at.exception
    assert not at.error
