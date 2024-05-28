import os
import pytest
from streamlit.testing.v1 import AppTest
from tests.base_pytest import start_authenticated_app_test
from modules.smz.smz_graphqa_chain import SmzGraphQAChain
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.components import GraphDatabaseConnection


# from "pages.5_Chat met neo4j" import Neo4JChatPage


@pytest.fixture(name="at")
def fixture_at():
    return start_authenticated_app_test("src/pages/5_Chat met neo4j.py")


@pytest.fixture(scope="function", autouse=True)
def setup_neo4j_connection(at, request):
    """Sets up the state for the test, like if the user connected to the neo4j instance in the Graph manager interface."""
    if "noautofixt" not in request.keywords:
        at.text_input("custom_neo4j_url").set_value(os.getenv("NEO4J_CONNECTION_URI"))
        at.text_input("custom_neo4j_username").set_value(os.getenv("NEO4J_USER"))
        at.text_input("custom_neo4j_password").set_value(os.getenv("NEO4J_PASSWORD"))
        at.button(
            "FormSubmitter:custom_graph_db_connection_settings-Submit"
        ).click().run(timeout=600)


@pytest.mark.noautofixt
def test_admin_chat_met_neo4j_page_load(at):

    assert (
        at.session_state.username in BaseUWVGraphPage._admin_users
    ), "The user is not an admin."
    assert not at.exception
    assert not at.error
    assert (
        at.warning[0].body
        == "**Let op:** deze Neo4J database wordt ook gebruikt voor andere test doeleinden.De database wordt vaak geleegd. Maak een eigen Neo4J database aan en vul de login details hieronder in."
    )


@pytest.mark.noautofixt
def test_deelnemer_chat_no_access():

    at = AppTest.from_file("src/pages/5_Chat met neo4j.py")
    at.run(timeout=600)
    assert at.button(key="FormSubmitter:Login-Login")

    login_button = at.button(key="FormSubmitter:Login-Login")
    if login_button:
        at.text_input[0].set_value("deelnemer")
        at.text_input[1].set_value("i8Fi/BYxOJgySNS9yjMRs")
        login_button.click().run(timeout=600)

    assert (
        at.session_state.username not in BaseUWVGraphPage._admin_users
    ), "The user is an admin."
    assert at.error
    assert at.error[0].body == "Je hebt geen toegang tot deze pagina."


def test_neo4j_ask_wrong_question(at):

    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)

    last_answer = at.session_state["neo4j_custom_chat_history"]["chat_history"][
        -1
    ].content
    assert (
        last_answer == SmzGraphQAChain.DEFAULT_ANSWER
    ), "The answer to the question was not the default answer."


def test_empty_chat_history_button(at):

    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)
    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)

    assert at.button("clear_chat")

    at.button("clear_chat").click().run(timeout=600)

    assert len(at.session_state["neo4j_custom_chat_history"]["chat_history"]) == 0
