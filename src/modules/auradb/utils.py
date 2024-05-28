from typing import List
import pandas as pd
from langchain.graphs.graph_document import GraphDocument


def combine_graph_documents(graphs: List[GraphDocument]) -> GraphDocument:
    """
    Combines multiple graphs into one.

    Args:
        graphs (List[GraphDocument]): The graphs to be combined.

    Returns:
        GraphDocument: The combined graph.
    """

    if len(graphs) == 0:
        raise ValueError("No graphs provided.")

    nodes = []
    relationships = []
    source = None
    for graph in graphs:
        nodes.append(graph.nodes)
        relationships.append(graph.relationships)
        source = graph.source

    return GraphDocument(nodes=nodes, relationships=relationships, source=source)


def graph_to_frame(graph: GraphDocument) -> List[pd.DataFrame]:
    """
    Converts a knowledge graph to a Pandas DataFrame.

    Args:
        graph (KnowledgeGraph): The knowledge graph to be converted.

    Returns:
        pd.DataFrame: The converted DataFrame.
    """

    props = []
    nodes = []
    for node in graph.nodes:
        nodes.append({"id": node.id, "type": node.type})
        if len(node.properties) > 0:
            # iterate key values pair in node.properties
            for key, value in node.properties.items():
                props.append(
                    {
                        "id": node.id,
                        "key": key,
                        "value": value,
                    }
                )

    relationships = []
    for rel in graph.relationships:
        relationships.append(
            {
                "Source node": rel.source.id,
                "Relation": rel.type,
                "Target node": rel.target.id,
            }
        )

    df_nodes = pd.DataFrame(nodes)
    df_relationships = pd.DataFrame(relationships)
    df_props = pd.DataFrame(props)

    return (
        df_nodes,
        df_relationships,
        df_props,
    )
