import os

import sys
from io import StringIO
from operator import itemgetter
from typing import List
from langchain.globals import set_debug
from langchain.chains import GraphCypherQAChain
from langchain_core.output_parsers import StrOutputParser
from langchain_community.graphs import Neo4jGraph
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
    Runnable,
    RunnableParallel,
    RunnableBranch,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from modules.smz.prompts import (
    CYPHER_GENERATION_PROMPT,
    CONTEXTUALIZE_QUESTION_GENERATION_PROMPT,
)


class SmzGraphQAChain:
    DEFAULT_ANSWER = "Ik heb geen antwoord op je vraag kunnen vinden in de Knowledge Graph. Probeer het anders te formuleren, verduidelijk je vraag, of stel een andere vraag 👍"
    _chain: RunnableParallel = None
    _graph: Neo4jGraph = None
    _capture_output: bool = True

    def __init__(self, llm, graph: Neo4jGraph, capture_output: bool = True):

        if not isinstance(graph, Neo4jGraph):
            raise ValueError("The graph should be an instance of Neo4jGraph")

        self._capture_output = capture_output
        self._graph = graph

        contextualize_q_chain = self.setup_contextualizing_question_chain(llm)

        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum, answer in Dutch and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        def contextualized_question(intermediate_result: dict):
            """
            If there's a chat history, condense the question to a standalone question.
            """
            chat_history = intermediate_result.get("chat_history")
            if len(chat_history) == 0 or (
                (len(chat_history) == 1) and (isinstance(chat_history[0], AIMessage))
            ):
                return intermediate_result["question"]

            return contextualize_q_chain

        graph.refresh_schema()

        graph_qa_chain = GraphCypherQAChain.from_llm(
            llm,
            graph=graph,
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            validate_cypher=True,
            return_direct=True,
            return_intermediate_steps=True,
            verbose=os.getenv("VERBOSE") == "1",
        )

        def get_cypher_query(intermediate_result, **kwargs):
            print(intermediate_result)
            if (
                "graphqa" in intermediate_result
                and "intermediate_steps" in intermediate_result["graphqa"]
                and "query" in intermediate_result["graphqa"]["intermediate_steps"][0]
            ):
                print(intermediate_result["graphqa"]["intermediate_steps"][0]["query"])
                return intermediate_result["graphqa"]["intermediate_steps"][0]["query"]
            return None

        # self._chain = RunnablePassthrough.assign(
        #     context=contextualized_question | graph_qa_chain
        # ) | RunnableParallel(
        #     query=itemgetter("query"),
        #     context=itemgetter("context"),
        #     response=RunnableBranch(
        #         # If the cypher chain does not give any results, return the default answer
        #         (
        #             lambda x: ("context" in x)
        #             and ("result" in x["context"])
        #             and (len(x["context"]["result"]) == 0),
        #             lambda y: self.DEFAULT_ANSWER,
        #         ),
        #         # Otherwise, formulate an answer using the LLM
        #         (qa_prompt | llm) | StrOutputParser(),
        #     ),
        # )
        # self._chain = (
        #     contextualized_question
        #     | graph_qa_chain
        #     # | RunnablePassthrough.assign(context=itemgetter("context"))
        #     | RunnableParallel(
        #         query=itemgetter("query"),
        #         context=itemgetter("result"),
        #         response=RunnableBranch(
        #             # If the cypher chain does not give any results, return the default answer
        #             (
        #                 lambda x: ("context" in x)
        #                 and ("result" in x["context"])
        #                 and (len(x["context"]["result"]) == 0),
        #                 lambda y: self.DEFAULT_ANSWER,
        #             ),
        #             # Otherwise, formulate an answer using the LLM
        #             (qa_prompt | llm) | StrOutputParser(),
        #         ),
        #     )
        # )

        def unpack_graphqa(intermediate_result: dict):
            if (
                "graphqa" in intermediate_result
                and "intermediate_steps" in intermediate_result["graphqa"]
                and "query" in intermediate_result["graphqa"]["intermediate_steps"][0]
            ):
                results = intermediate_result["graphqa"]["intermediate_steps"][0]
                return {
                    "question": intermediate_result["question"],
                    "chat_history": intermediate_result["chat_history"],
                    "context": intermediate_result["graphqa"]["result"],
                    "contextualised_question": intermediate_result["graphqa"]["query"],
                    "cypher": results["query"],
                }
            return None

        self._chain = (
            RunnablePassthrough.assign(graphqa=contextualized_question | graph_qa_chain)
            | RunnableLambda(unpack_graphqa)
            | RunnableParallel(
                cypher=itemgetter("cypher"),
                context=itemgetter("context"),
                contextualised_question=itemgetter("contextualised_question"),
                response=RunnableBranch(
                    # If the cypher chain does not give any results, return the default answer
                    (
                        lambda x: ("context" in x) and (len(x["context"]) == 0),
                        lambda y: self.DEFAULT_ANSWER,
                    ),
                    # Otherwise, formulate an answer using the LLM
                    (qa_prompt | llm) | StrOutputParser(),
                ),
            )
        )

        # self._chain.get_graph().print_ascii()

    def ask(self, question: str, chat_history: List = []) -> str:
        if not self._chain:
            raise ValueError("Chain not setup yet")

        # Create a StringIO object to capture stdout
        if self._capture_output:
            stdout_capture = StringIO()
            sys.stdout = stdout_capture

            set_debug(True)

        result = self._chain.invoke(
            {"question": question, "chat_history": chat_history}
        )

        if self._capture_output:
            set_debug(False)

            # Get the captured stdout as a string
            stdout_string = stdout_capture.getvalue()

            # Reset stdout to its original value
            sys.stdout = sys.__stdout__

            result["debug"] = stdout_string
        else:
            result["debug"] = "No output captured."

        return result

    def setup_contextualizing_question_chain(self, llm):

        return CONTEXTUALIZE_QUESTION_GENERATION_PROMPT | llm | StrOutputParser()
