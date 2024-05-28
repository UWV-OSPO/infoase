# pylint: disable=E1129
import os
import json
import warnings
from typing import List
from neo4j import GraphDatabase, Driver
from neo4j.graph import Node as Neo4JNode, Relationship as Neo4JRelationship
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship


class AuraDB:
    """A class to interact with the Neo4J AuraDB database"""

    _driver: Driver = None

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(
            uri, auth=(user, password), max_connection_lifetime=200
        )

    def check_status(self):
        """
        Checks the status of the database connection.

        Raises:
            Exception: If the connection is not open.
        """

        with self._driver:
            self._driver.verify_connectivity()

    def cleanup(self) -> None:
        """Removes all nodes, relationships and properties from the database.

        Also see:
        https://aura.support.neo4j.com/hc/en-us/articles/360059882854-Using-APOC-periodic-iterate-to-delete-large-numbers-of-nodes
        """
        with self._driver:
            with self._driver.session() as session:
                session.run(
                    "MATCH ()-[r]->() CALL { WITH r DELETE r } IN TRANSACTIONS OF 50000 ROWS;"
                )
                session.run(
                    "MATCH (n) CALL { WITH n SET n = {} } IN TRANSACTIONS OF 50000 ROWS;"
                )
                session.run(
                    "MATCH (n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 50000 ROWS;"
                )

    def export_jsonl(self, filename: str = "tmp/export.jsonl") -> None:
        """
        Exports the entire database to a JSON file.

        Args:
            filename (str): The filename to export to. Defaults to "tmp/export.json".

        Returns:
            None
        """

        with self._driver:
            with self._driver.session() as session:
                result = session.run(
                    """
                        CALL apoc.export.json.all(null, {stream:true})
                        YIELD file, nodes, relationships, properties, data
                        RETURN file, nodes, relationships, properties, data
                    """
                )
                result = result.single()

                with open(filename, "w", encoding="utf-8") as file:
                    file.write(result["data"])

    # def import_jsonl(self, json_lines: List[dict]) -> dict:
    #     """Imports a list of json objects into the database.

    #     Args:
    #         json_lines (List[dict]): A list of dictionaries containing the data to import.

    #     Returns:
    #         dict: A dict with the number of nodes and relationships that were created.
    #     """

    #     def add_node(tx, node_data) -> int:
    #         labels = ":".join(node_data["labels"])
    #         query = (
    #             f"MERGE (n:{labels} {{id: $id}}) "
    #             "ON CREATE SET n = $properties, n._created = true "
    #             "RETURN n._created IS NOT NULL as created"
    #         )
    #         result = tx.run(
    #             query,
    #             id=node_data["id"],
    #             properties=node_data["properties"],
    #         )
    #         return int(result.single()[0])

    #     def add_relationship(tx, rel_data):
    #         rel_type = rel_data["label"]
    #         query = (
    #             "MATCH (a {id: $start_id}), (b {id: $end_id}) "
    #             f"MERGE (a)-[r:{rel_type}]->(b) "
    #             "ON CREATE SET r._created = true "
    #             "RETURN r._created IS NOT NULL as created"
    #         )
    #         result = tx.run(
    #             query,
    #             start_id=rel_data["start"]["properties"]["id"],
    #             end_id=rel_data["end"]["properties"]["id"],
    #         )
    #         return int(result.single()[0])

    #     node_count = 0
    #     relationship_count = 0

    #     for data in json_lines:
    #         with self._driver:
    #             with self._driver.session() as session:
    #                 # Now create nodes and relationships and count them.
    #                 if data["type"] == "node":
    #                     node_count += session.execute_write(add_node, data)
    #                 elif data["type"] == "relationship":
    #                     relationship_count += session.execute_write(
    #                         add_relationship, data
    #                     )

    #     return {"node_count": node_count, "relationship_count": relationship_count}

    def import_list(self, graph_objs: List[dict]) -> None:
        """Imports a list of json objects into the database.

        Args:
            json_lines (List[dict]): A list of dictionaries containing the data to import.

        Returns:
            dict: A dict with the number of nodes and relationships that were created.
        """

        def add_node(tx, node: Node) -> dict:
            query = (
                f"MERGE (n:{node.type} {{id: $id}}) "
                "ON CREATE SET n = $properties, n.id = $id, n._created = true "
                "ON MATCH SET n += $properties "
                "RETURN id(n) as node_id, n._created AS created"
            )
            result = tx.run(
                query,
                id=node.id,
                properties=node.properties,
            )
            record = result.single()
            if record:
                return {
                    "node_id": record["node_id"],
                    "created": record["created"],
                }

            warnings.warn(f"🔴 Failed to create or match node with id '{node.id}'")
            return None

        def add_relationship(tx, rel: Relationship):
            query = (
                "MATCH (a) WHERE a.id = $start_id "
                "MATCH (b) WHERE b.id = $end_id "
                "WITH a, b "
                f"MERGE (a)-[r:{rel.type}]->(b) "
                "ON CREATE SET r = $properties "
                "ON MATCH SET r += $properties "
                "RETURN id(a) as start_id, id(b) as end_id, id(r) as rel_id, r._created as created"
            )
            result = tx.run(
                query,
                start_id=rel.source.id,
                end_id=rel.target.id,
                properties=rel.properties if rel.properties is not None else {},
            )
            record = result.single()
            if record:
                return {
                    "start_id": record["start_id"],
                    "end_id": record["end_id"],
                    "rel_id": record["rel_id"],
                    "created": record["created"],
                }

            # This block is reached if the nodes don't exist and hence no relationship is created
            warnings.warn(
                f"🔴 Cannot create relationship {rel.type} because one or both nodes do not exist"
            )
            return None

        with self._driver:
            with self._driver.session() as session:
                for obj in graph_objs:
                    if isinstance(obj, Node):
                        session.execute_write(add_node, obj)
                    elif isinstance(obj, Relationship):
                        session.execute_write(add_relationship, obj)

    # def import_file(self, filename: str) -> dict:
    #     if not os.path.exists(filename):
    #         raise FileNotFoundError(f"File {filename} does not exist")
    #     if not filename.endswith(".json"):
    #         raise ValueError(f"File {filename} is not a JSON file")

    #     json_lines = []
    #     with open(filename, "r", encoding="utf-8") as file:
    #         for line in file:
    #             # The file contains one JSON object per line, load it.
    #             json_lines.append(json.loads(line))

    #     return self.import_jsonl(json_lines)

    def get_knowledge_graph(self):
        with self._driver:
            with self._driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    OPTIONAL MATCH (n)-[r]->(m)
                    RETURN
                        collect(DISTINCT {id: n.id, type: head(labels(n)), properties: apoc.map.removeKey(COALESCE(properties(n), {}), '_created')}) AS nodes,
                        collect(DISTINCT {id: id(r), start_node_id: startNode(r).id, end_node_id: endNode(r).id, type: type(r), properties: apoc.map.removeKey(COALESCE(properties(r), {}), '_created')}) AS relationships
                    """
                ).single()

        nodes_data = result["nodes"]
        relationships_data = result["relationships"]

        # Convert nodes to Node objects
        node_dict = {
            node["id"]: Node(
                id=node["id"],
                type=node["type"],
                properties=node["properties"],
            )
            for node in nodes_data
        }

        # Convert relationships to Relationship objects
        relationship_list = [
            Relationship(
                source=node_dict.get(rel["start_node_id"]),
                type=rel["type"],
                target=node_dict.get(rel["end_node_id"]),
                properties=rel["properties"],
            )
            for rel in relationships_data
            if rel["id"] is not None
        ]

        graph_dict = {
            "nodes": list(node_dict.values()),
            "relationships": relationship_list,
        }
        return graph_dict
