from uwv_toolkit.utils import azure_llm


def test_temperature():
    llm = azure_llm(temperature=0)

    result1 = llm.invoke("Dit is een test")
    result2 = llm.invoke("Dit is een test")

    assert result1 == result2
