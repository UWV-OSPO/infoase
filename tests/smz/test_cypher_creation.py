import os
import pytest
from langchain.chains import GraphCypherQAChain
from modules.smz import SmzGraphQAChain
from modules.smz.prompts import CYPHER_GENERATION_PROMPT
from uwv_toolkit.utils import azure_llm


@pytest.fixture(name="chain")
def fixture_chain(neo4j_graph):
    llm = azure_llm(temperature=0)
    return SmzGraphQAChain(llm=llm, graph=neo4j_graph, capture_output=False)


def cypher_chain(neo4j_graph):
    llm = azure_llm(temperature=0)
    graph_qa_chain = GraphCypherQAChain.from_llm(
        llm,
        graph=neo4j_graph,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        validate_cypher=True,
        return_direct=True,
        return_intermediate_steps=True,
        verbose=os.getenv("VERBOSE") == "1",
    )

    return graph_qa_chain


def test_cypher_chain(neo4j_graph):
    chain = cypher_chain(neo4j_graph)

    result = chain.invoke("Wat doet een bedrijfsarts?")

    print("#########################")
    print(result)
