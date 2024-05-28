import time
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from modules.smz import SmzGraphQAChain
from uwv_toolkit.utils import azure_llm


@pytest.fixture(name="chain")
def fixture_chain(neo4j_graph):
    llm = azure_llm(temperature=0)
    return SmzGraphQAChain(llm=llm, graph=neo4j_graph, capture_output=False)


def test_graph_qa_chain(walterbob_graph, chain):
    time.sleep(10)
    question = "Who is Walter?"
    chat_history = []

    answer = chain.ask(
        question=question,
        chat_history=chat_history,
    )
    assert "Walter" in answer["response"]


def test_graph_qa_chain_irrelevant(chain, walterbob_graph):
    question = "Vertel me over de relativiteitstheorie van Einstein."
    chat_history = []

    answer = chain.ask(
        question=question,
        chat_history=chat_history,
    )

    assert answer["response"] == chain.DEFAULT_ANSWER


def test_whos_bob_test(chain, walterbob_graph):
    question = "Who is Bob?"
    chat_history = []

    answer = chain.ask(
        question=question,
        chat_history=chat_history,
    )
    print(answer)
    assert "Bob" in answer["response"]


def test_history_chain(chain, walterbob_graph):
    question = "Where does he live?"
    chat_history = [
        AIMessage(content="Hi, wat kan ik voor je betekenen?"),
        HumanMessage(content="Who is Bob?"),
        AIMessage(content="Bob is a person."),
    ]

    answer = chain.ask(
        question=question,
        chat_history=chat_history,
    )
    print("ANSWER", answer)
    # assert "Amsterdam" in answer["response"]


def test_disney_chain(chain, waltdisney_graph):
    question = "Who is Walt?"
    chat_history = []

    answer = chain.ask(
        question=question,
        chat_history=chat_history,
    )
    print(answer)
    assert "Walt Disney" in answer["response"]
