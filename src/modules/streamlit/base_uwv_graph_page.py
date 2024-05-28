import os
import streamlit as st
import pandas as pd
from typing import List
from langchain_community.graphs.graph_document import GraphDocument
from uwv_toolkit.streamlit.page import BaseAuthenticatedPage
from modules.streamlit.utils import is_admin, is_authenticated

# from modules.streamlit.graph_chart import GraphChart


class BaseUWVGraphPage(BaseAuthenticatedPage):

    _admin_users = [
        "michiel.buisman",
        "jelle.kruizinga",
        "thomas.vedder",
        "bas.wenneker",
        "lars.hulzebos",
    ]

    def _show_menu(self):

        if os.getenv("ENVIRONMENT") != "test":
            st.sidebar.page_link("Home.py", label="Home", icon="🏠")

            if is_authenticated():

                if is_admin(self._admin_users):
                    st.sidebar.page_link(
                        "pages/1_Tekst naar KG.py",
                        label="🔒 Tekst naar KG",
                    )
                    st.sidebar.page_link(
                        "pages/2_Document naar KG.py",
                        label="🔒 Document naar KG",
                    )
                    st.sidebar.page_link(
                        "pages/3_Graph manager.py",
                        label="🔒 Graph manager",
                    )
                    st.sidebar.page_link(
                        "pages/Feedback.py",
                        label="🔒 Feedback",
                    )
                    st.sidebar.page_link(
                        "pages/5_Chat met neo4j.py",
                        label="🔒 Chat met Neo4J (Ontwikkel)",
                    )

                st.sidebar.page_link(
                    "pages/4_Chat met docs.py",
                    label="💬 Chat met docs",
                )
                st.sidebar.page_link(
                    "pages/6_Chat met neo4j prod.py",
                    label="💬 Chat met Neo4J",
                )

    def show_knowledge_graph(self, documents: List[GraphDocument]):
        """
        Helper method to show the knowledge graph in Streamlit.
        """
        nodes = []
        relationships = []
        properties = []
        for doc in documents:
            for node in doc.nodes:
                nodes.append({"id": node.id, "type": node.type})
                properties.extend(
                    [
                        {"Node": node.id, "Property": prop, "Waarde": value}
                        for prop, value in node.properties.items()
                    ]
                )

            relationships.extend(
                [
                    {
                        "Source node": rel.source.id,
                        "Type": rel.type,
                        "Target node": rel.target.id,
                    }
                    for rel in doc.relationships
                ]
            )

        # if len(documents) > 0:
        #     with st.expander("Graph", expanded=False):
        #         graph_chart = GraphChart(nodes=nodes, edges=relationships)
        #         graph_chart.show(add_container=False)

        if len(nodes) > 0:
            with st.expander("Nodes", expanded=False):
                df_nodes = pd.DataFrame(nodes)
                st.dataframe(df_nodes)
        else:
            st.warning("No nodes found.")

        if len(relationships) > 0:
            with st.expander("Relationships", expanded=False):
                df_relationships = pd.DataFrame(relationships)
                st.dataframe(df_relationships)
        else:
            st.warning("No relationships found.")

        if len(properties) > 0:
            with st.expander("Eigenschappen", expanded=False):
                st.dataframe(properties)
        else:
            st.warning("No properties found.")
