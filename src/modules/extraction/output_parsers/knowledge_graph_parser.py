import warnings
import re
import json
from typing import List
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from src.modules.extraction.prompts import few_shot_prompt_examples, system_prompt


class KnowledgeGraphParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        output_pattern = r"\[\s*['\"].+?['\"]\s*,\s*['\"].+?['\"]\s*,\s*\{.*?\}\]"

        try:
            nodes_text = text.split("Nodes:")[1].split("Relationships:")[0]
            relationships_text = text.split("Relationships:")[1]
        except IndexError as e:
            raise OutputParserException(
                """Could not parse Nodes and Relationships strings from output. Structure of the answer is not in the correct schema. Expected output schema:
                Nodes: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]
                Relationships: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]"""
            ) from e

        if not nodes_text or not relationships_text:
            raise OutputParserException(
                """Could not parse Nodes and Relationships strings from output.
                Structure of the answer is not in the correct schema. Expected output schema:
                Nodes: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]
                Relationships: [[ENTITY_ID_1, RELATIONSHIP, ENTITY_ID_2, PROPERTIES], ...]"""
            )

        nodes_rows = re.findall(output_pattern, nodes_text)
        nodes = self._parse_nodes(nodes_rows)

        relationship_rows = re.findall(output_pattern, relationships_text)
        relationships = self._parse_relationships(relationship_rows, nodes)

        return {"nodes": list(nodes.values()), "relationships": relationships}

    def get_format_instructions(self) -> str:
        return (
            system_prompt
            + "\n\nHere's an example conversation with responses in the valid format:\n"
            + few_shot_prompt_examples.format()
        )

    @property
    def _type(self) -> str:
        return "boolean_output_parser"

    def _parse_nodes(self, node_rows: List[str]) -> dict[Node]:
        node_pattern = r"\[['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"],\s*(\{.*?\})\]"

        result = {}
        for row in node_rows:
            node_match = re.match(node_pattern, row)

            if node_match is None:
                raise OutputParserException(f"🔴 Cound not parse node {row}")

            name = node_match.group(1)
            node_id = name.lower().replace(" ", "_")
            node_type = node_match.group(2).title()

            properties = node_match.group(3)
            properties = properties.replace("'", '"')
            try:
                properties = json.loads(properties)
                if "name" not in properties:
                    if "naam" in properties:
                        properties["name"] = properties["naam"]
                        del properties["naam"]
                    else:
                        properties["name"] = name
            except ValueError as e:
                warnings.warn(f"🔴 Error parsing node properties of {row}, error: {e}.")
                properties = {"name": name}

            result[node_id] = Node(id=node_id, type=node_type, properties=properties)

        return result

    def _parse_relationships(
        self, rel_rows: List[str], nodes: dict[Node]
    ) -> List[Relationship]:
        rel_pattern = r"\[['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"],\s*({[^}]*})"

        result = []
        for row in rel_rows:
            matches = re.search(rel_pattern, row)
            if matches is None:
                raise OutputParserException(f"🔴 Cound not parse rel {row}")

            source_id = matches.group(1).lower().replace(" ", "_")
            if source_id not in nodes:
                warnings.warn(
                    f"🔴 Cound not find relationship {source_id}"
                    + f" in nodes list: {nodes}."
                )
                continue

            source_node = nodes[source_id]

            target_id = matches.group(3).lower().replace(" ", "_")
            if target_id not in nodes:
                warnings.warn(
                    f"🔴 Cound not find relationship target {target_id}"
                    + f" in nodes list: {nodes}."
                )
                continue

            target_node = nodes[target_id]
            reltype = matches.group(2)

            properties = matches.group(4)
            properties = properties.replace("'", '"')
            try:
                properties = json.loads(properties)
            except ValueError as e:
                warnings.warn(f"🔴 Error parsing relationship of {row}, error: {e}.")
                properties = {}

            result.append(
                Relationship(
                    source=source_node,
                    target=target_node,
                    type=reltype,
                    properties=properties,
                )
            )
        return result
