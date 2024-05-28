import pytest
from langchain_core.messages import AIMessage
from tests.base_pytest import start_authenticated_app_test, enable_caching
from modules.smz import SmzDocChain as Chain
from uwv_toolkit.db import BaseModel

enable_caching()


@pytest.fixture(scope="module", name="at")
def fixture_at():
    return start_authenticated_app_test("src/pages/4_Chat met docs.py")


def test_doc_chat_load(at):
    assert not at.exception
    assert not at.error


def test_home_ask_wrong_question(at):
    at.chat_input[0].set_value("Vertel iets over de relativiteitstheorie.").run(
        timeout=600
    )
    assert at.session_state["doc_chat_history"]["chat_history"][-1] == AIMessage(
        content="Ik heb geen antwoord op je vraag kunnen vinden in de documenten die ik ken. Probeer het anders te formuleren, of stel een andere vraag 👍"
    )


def test_feedback(at, mocker):

    assert not at.session_state["doc_chat_history"]["feedback_submitted"]

    mocker.patch.object(
        Chain,
        "ask",
        return_value={
            "response": "Thanks voor je vraag",
            "context": [],
            "debug": "Debug info",
        },
    )

    mocked_feedback_model = mocker.patch.object(BaseModel, "save")

    query = "Vertel over opleiding kosten."
    at.chat_input[0].set_value(query).run(timeout=600)

    feedback_expander = at.main.chat_message[-1].children[1]
    assert feedback_expander.type == "expandable"

    at.main.chat_message[-1].radio("fb_positive").set_value("👎 Nee")
    at.main.chat_message[-1].text_area("fb_answer").set_value(
        "Het antwoord was niet goed."
    )
    at.main.chat_message[-1].text_area("fb_remark").set_value(
        "Meer informatie over de kosten."
    )
    at.main.chat_message[-1].text_input("fb_email").set_value("steve@apple.com")
    at.main.chat_message[-1].button(
        "FormSubmitter:feedback_form-Verstuur feedback"
    ).click().run(timeout=600)

    assert mocked_feedback_model.assert_called_once
