import os
from typing import List, Iterator, Dict, Any, Optional
from uuid import UUID
from operator import itemgetter

import sys
from io import StringIO
from langchain.globals import set_debug

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableBranch,
    RunnableParallel,
)


class SmzDocChain:
    DEFAULT_ANSWER = "Ik heb geen antwoord op je vraag kunnen vinden in de documenten die ik ken. Probeer het anders te formuleren, of stel een andere vraag 👍"
    score_threshold = 0.7
    k = 5
    _retriever: VectorStoreRetriever = None
    _chain: RunnableParallel = None

    def __init__(
        self,
        vectorstore: VectorStore,
        llm,
        score_threshold: float = None,
        k: int = None,
    ):
        if score_threshold is not None:
            self.score_threshold = score_threshold
        if k is not None:
            self.k = k

        self._retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": self.score_threshold, "k": self.k},
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        def contextualized_question(intermediate_result: dict):
            if intermediate_result.get("chat_history"):
                return contextualize_q_chain
            else:
                return intermediate_result["question"]

        self._chain = RunnablePassthrough.assign(
            context=contextualized_question | self._retriever
        ) | RunnableParallel(
            context=itemgetter("context"),
            response=RunnableBranch(
                (lambda x: len(x["context"]) == 0, lambda y: self.DEFAULT_ANSWER),
                (
                    RunnablePassthrough(context=lambda x: format_docs(x["context"]))
                    | qa_prompt
                    | llm
                )
                | StrOutputParser(),
            ),
        )

    def ask(self, question: str, chat_history: List = []) -> Iterator:
        if not self._retriever:
            raise ValueError("Retriever not setup yet")
        if not self._chain:
            raise ValueError("Chain not setup yet")

        # Create a StringIO object to capture stdout
        stdout_capture = StringIO()
        sys.stdout = stdout_capture

        set_debug(True)

        result = self._chain.invoke(
            {"question": question, "chat_history": chat_history}
        )
        set_debug(False)

        # Get the captured stdout as a string
        stdout_string = stdout_capture.getvalue()

        # Reset stdout to its original value
        sys.stdout = sys.__stdout__
        result["debug"] = stdout_string
        return result
