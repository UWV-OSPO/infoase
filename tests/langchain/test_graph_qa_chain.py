def test_cypher_chain_walter(cypher_chain, walterbob_graph):

    answer = cypher_chain.invoke("Who is Walter?")
    assert "Walter" in answer["result"]
    assert "Delft" in answer["result"]


def test_cypher_chain_w(cypher_chain, walterbob_graph):
    answer = cypher_chain.invoke("Who's name starts with W?")
    assert "Walter" in answer["result"]


def test_cypher_chain_bob(cypher_chain, walterbob_graph):
    answer = cypher_chain.invoke("Who is Bob?")
    assert "35" in answer["result"]


def test_cypher_chain_friends(cypher_chain, walterbob_graph):
    answer = cypher_chain.invoke("Does Walter have any friends?")
    assert "Bob" in answer["result"]


def test_load_waltgraph(waltdisney_graph, cypher_chain):

    answer = cypher_chain.invoke("Is er iemand wiens naam lijkt op de naam Walter?")
    print(answer)
