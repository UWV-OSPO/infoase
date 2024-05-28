import os
import pytest
from streamlit.testing.v1 import AppTest
from tests.base_pytest import start_authenticated_app_test
from modules.smz.smz_graphqa_chain import SmzGraphQAChain
from modules.streamlit.base_uwv_graph_page import BaseUWVGraphPage
from modules.streamlit.components import GraphDatabaseConnection


PAGE_FILE = "src/pages/6_Chat met neo4j prod.py"


@pytest.fixture(name="at")
def fixture_at():
    return start_authenticated_app_test(PAGE_FILE)


def test_admin_chat_met_neo4j_page_load(at):

    assert (
        at.session_state.username in BaseUWVGraphPage._admin_users
    ), "The user is not an admin."
    assert not at.exception
    assert not at.error

    assert len(at.warning) == 1
    assert (
        at.warning[0].body
        == "**Let op:** deze Neo4J database wordt ook gebruikt voor andere test doeleinden.De database wordt vaak geleegd. Maak een eigen Neo4J database aan en vul de login details hieronder in."
    )
    assert len(at.success) > 0
    assert at.success[0].body == "🟢 Verbonden met Neo4J (Productie)."


def test_deelnemer_chat():

    at = AppTest.from_file(PAGE_FILE)
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
    assert not at.exception
    assert not at.error

    assert len(at.warning) == 1
    assert (
        at.warning[0].body
        == "**Let op:** deze Neo4J database wordt ook gebruikt voor andere test doeleinden.De database wordt vaak geleegd. Maak een eigen Neo4J database aan en vul de login details hieronder in."
    ), "The warning about the test db is not shown."

    assert at.success[0].body == "🟢 Verbonden met Neo4J (Productie)."


def test_neo4j_ask_wrong_question(at):

    assert at.session_state.prod_graph_db_connection.is_connected()
    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)

    assert (
        at.session_state["neo4j_prod_chat_history"]["chat_history"][-1].content
        == SmzGraphQAChain.DEFAULT_ANSWER,
        "The answer to the question was not the default answer.",
    )


def test_empty_chat_history_button(at):

    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)
    at.chat_input[0].set_value("Een ijsbeer leeft in alaska.").run(timeout=600)

    assert at.button("clear_chat")

    at.button("clear_chat").click().run(timeout=600)

    assert len(at.session_state["neo4j_prod_chat_history"]["chat_history"]) == 0
