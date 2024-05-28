import pytest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from typing import List
from src.modules.extraction.output_parsers import KnowledgeGraphParser
from langchain_community.graphs.graph_document import Node, Relationship
from src.modules.extraction.prompts import extraction_prompt

from langchain_core.exceptions import OutputParserException


@pytest.fixture(name="parser")
def fixture_parser():
    return KnowledgeGraphParser()


@pytest.fixture(name="alice_and_bob")
def fixture_alice_and_bob(parser) -> tuple[list, list]:
    result = parser.parse(
        """
    Nodes: [['Alice', 'Person', {"location": 'Delft'}], ['Bob', 'Person', {"birthday": '13-1-1986'}]]
    Relationships: [['Alice', 'KNOWS', 'Bob', {}]]"""
    )
    nodes = result["nodes"]
    relationships = result["relationships"]
    return nodes, relationships


@pytest.fixture(name="nodes")
def fixture_alice_and_bob_nodes(alice_and_bob) -> List:
    nodes, _ = alice_and_bob
    return nodes


@pytest.fixture(name="relationships")
def fixture_alice_and_bob_relationships(alice_and_bob) -> List:
    _, relationships = alice_and_bob
    return relationships


def test_parsing_nodes(nodes):
    assert len(nodes) == 2
    alice = nodes[0]

    assert isinstance(alice, Node)
    assert alice.id == "alice"
    assert alice.type == "Person"
    assert alice.properties.keys() == {"location", "name"}
    assert alice.properties["location"] == "Delft"
    assert alice.properties["name"] == "Alice"


def test_parsing_relationships(relationships):
    assert len(relationships) == 1
    relationship = relationships[0]

    assert isinstance(relationship, Relationship)
    assert relationship.source.id == "alice"
    assert isinstance(relationship.source, Node)
    assert isinstance(relationship.target, Node)
    assert relationship.target.id == "bob"
    assert relationship.type == "KNOWS"
    assert relationship.properties == {}


def test_node_parsing(alice_and_bob):
    nodes, relationships = alice_and_bob
    assert len(nodes) == 2
    assert len(relationships) == 1


def test_relationship_parsing(parser):
    result = parser.parse(
        """
    Nodes: [['Walter Disney', 'Person', {"name": 'Walter'}], ['Bob', 'Person', {"name": 'Bob'}]]
    Relationships: [['Walter Disney', 'KNOWS', 'Bob', {}]]"""
    )
    nodes = result["nodes"]
    relationships = result["relationships"]

    assert len(nodes) == 2
    assert len(relationships) == 1


def test_node_parsing_exception(parser):
    try:
        parser.parse(
            """
        Nodes: ['Walter Disney', 'Person', {"name": 'Walter'}]
        Relationships: [['Walter Disney', 'Bob', {}]]"""
        )
        assert False
    except OutputParserException:
        assert True


def test_relationship_parsing_exception(parser):
    try:
        parser.parse(
            """
        Nodes: [['Walter Disney', 'Person', {"name": 'Walter'}], ['Bob', 'Person', {"name": 'Bob'}]]
        Relationships: ['Walter Disney', 'Bob', {}]"""
        )
        assert False
    except OutputParserException as e:
        assert True


def test_relationship_parsing_error_fix2(parser):
    result = parser.parse(
        """
    Nodes: [['Walter Disney', 'Person', {"name": 'Walter'}], ['Bob', 'Person', {"name": 'Bob'}]]
    Relationships: [['Walter Disney', 'knows', 'Bob', {}]"""
    )
    relationships = result["relationships"]
    assert len(relationships) == 1


def test_parsing_error_invalid_props(parser):
    result = parser.parse(
        """
    Nodes: [['Walter Disney', 'Person', {"occupation": ['loodgieter', 'electricien']}]]
    Relationships: []"""
    )
    nodes = result["nodes"]
    assert len(nodes) == 1


def test_parsing_node_nam(parser):
    result = parser.parse(
        """
    Nodes: [['Walter Disney', 'Person', {"occupation": ['loodgieter', 'electricien']}]]
    Relationships: []"""
    )
    nodes = result["nodes"]
    assert nodes[0].properties["name"] == "Walter Disney"
