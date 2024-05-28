from modules.smz import SmzDocVector as Vector, SmzDocChain as Chain
from uwv_toolkit.utils import azure_llm

from tests.base_pytest import enable_caching

enable_caching()


def test_callbacks():
    llm = azure_llm()

    vectordb = Vector(documents=["data/test/disney_test_2p.pdf"]).setup()
    chain = Chain(vectorstore=vectordb, llm=llm)

    x = chain.ask(question="wie is disney")
    # print(x)
