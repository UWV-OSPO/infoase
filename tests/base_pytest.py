import sys
import os
import warnings
import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain.globals import set_verbose
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from streamlit.testing.v1 import AppTest
from src.modules.utils.load_env import load_env

load_env()

set_verbose((os.getenv("VERBOSE") == "1"))
# set_debug(True)


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture(name="neo4j_graph")
def fixture_neo4j_graph():
    connection_uri = os.getenv("NEO4J_CONNECTION_URI")
    username = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    return Neo4jGraph(url=connection_uri, username=username, password=password)


def enable_caching() -> None:
    """
    Enable caching for the app.

    Returns:
        None
    """
    set_llm_cache(SQLiteCache(database_path="tmp/.test_langchain.db"))


def start_authenticated_app_test(file: str) -> AppTest:
    at = AppTest.from_file(file, default_timeout=600)
    at.run()
    login_streamlit_authenticator(at)
    return at


def login_streamlit_authenticator(at: AppTest) -> None:
    """
    Login to the streamlit authenticator.

    Args:
        at (AppTest): The AppTest object to use.

    Returns:
        None
    """

    login_button = at.button(key="FormSubmitter:Login-Login")
    if login_button:
        at.text_input[0].set_value("michiel.buisman")
        at.text_input[1].set_value("OgUI1lQreZI-wkRw")
        login_button.click().run(timeout=600)
