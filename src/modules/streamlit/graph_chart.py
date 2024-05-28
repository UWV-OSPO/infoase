from typing import List
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from langchain.graphs.graph_document import GraphDocument
from colorhash import ColorHash


class GraphChart:
    _nodes: List
    _edges: List

    def __init__(self, nodes: List, edges: List):
        """
        Initializes the GraphChart.

        Args:
            graph_document (GraphDocument): The graph document to be visualized.
        """
        if len(nodes) == 0:
            raise ValueError("There are no documents.")

        self._nodes = nodes
        self._edges = edges

    # @staticmethod
    # def from_documents(documents: List[GraphDocument]):
    #     """
    #     Initializes the GraphChart from documents.

    #     Args:
    #         documents (List[GraphDocument]): The documents to be visualized.

    #     Returns:
    #         GraphChart: The graph chart.
    #     """
    #     return GraphChart(documents)

    def show(self, add_container: bool = True):
        """
        Shows the graph chart.
        """
        nodes = self._get_nodes()
        edges = self._get_edges()

        config = Config(
            width="100%",
            height=750,
            directed=False,
            physics=True,
            hierarchical=False,
            nodeSpacing=550,
            # **kwargs
        )

        if add_container:
            with st.container(border=True):
                agraph(nodes=nodes, edges=edges, config=config)
        else:
            agraph(nodes=nodes, edges=edges, config=config)

    def _get_nodes(self) -> List[Node]:
        nodes = []

        def get_contrast_color(r, g, b):
            # Calculate the luminance of the color
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

            # Choose black or white as the contrasting color
            if luminance > 0.5:
                return "#000000"  # Black
            else:
                return "#FFFFFF"  # White

        for node in self._nodes:
            # Node.type should define the color of the node.
            color = ColorHash(node.type)
            inverted_color = get_contrast_color(
                color.rgb[0], color.rgb[1], color.rgb[2]
            )

            label = f"{node.properties.get('name', node.id)} ({node.type})"

            nodes.append(
                Node(
                    id=node.id,
                    color=color.hex,
                    font={"color": inverted_color},
                    # size=200,
                    label=label,
                    shape="ellipse",
                )
            )

        return nodes

    def _get_edges(self) -> List[Edge]:
        edges = []

        for rel in self._edges:
            edges.append(
                Edge(
                    source=rel.source.id,
                    target=rel.target.id,
                    label=rel.type,
                    title=rel.type,
                )
            )

        return edges
