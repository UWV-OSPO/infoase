import json
import re
import warnings
import os
from typing import List

from langchain.schema import Document
from langchain.output_parsers import OutputFixingParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages.base import BaseMessage
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from .prompts import (
    extraction_prompt,
    generate_prompt_with_labels,
    generate_extraction_prompt,
)
from src.modules.extraction.output_parsers import KnowledgeGraphParser
from src.modules.extraction import BaseExtractor
from langchain.globals import set_debug, set_verbose
from modules.utils.load_env import load_env


load_env()
if os.environ["ENVIRONMENT"] == "development":
    set_debug(True)
    # set_verbose(True)


class FewShotDataExtractor(BaseExtractor):
    """
    This class extracts data from a document using a few-shot learning model.
    """

    # The llm to use for extraction.
    llm: BaseChatModel
    # Whether to print verbose output.
    verbose: bool
    _extraction_prompt: ChatPromptTemplate

    def __init__(
        self, llm: BaseChatModel, system_prompt: str = None, verbose: bool = False
    ) -> None:
        """
        Creates a new instance of the FewShotDataExtractor class.

        Args:
            llm (BaseChatModel): The language model to use for extraction.
            prompt (str, optional): The prompt to use for extraction. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        self.llm = llm
        self.verbose = verbose
        if system_prompt is not None:
            self._extraction_prompt = generate_extraction_prompt(system_prompt)
        else:
            self._extraction_prompt = extraction_prompt

    def run_list(self, data: List[Document]) -> List[GraphDocument]:
        chunked_data = self._chunk_documents(
            documents=data,
            llm=self.llm,
            messages=self._extraction_prompt.format_messages(input=""),
        )

        return self._run_chunked_data(chunked_data)

    def run(self, data: str) -> List[GraphDocument]:
        chunked_data = self._chunk_text(
            text=data,
            llm=self.llm,
            messages=self._extraction_prompt.format_messages(input=""),
        )

        return self._run_chunked_data(chunked_data)

    def _run_chunked_data(self, chunked_data: List[Document]) -> List[GraphDocument]:
        """
        Runs the extraction on the given data.

        Args:
            chunked_data (List[Document]): The chunked data to extract from.

        Returns:
            List[str]: The extracted data.
        """

        labels = set()
        result = []

        for index, chunk in enumerate(chunked_data):
            if self.verbose:
                print(f"🐢 Working on chunk {index+1}/{len(chunked_data)}.")

            llm_output = self._process_with_labels(chunk, list(labels))
            graph_document = GraphDocument(
                nodes=llm_output["nodes"],
                relationships=llm_output["relationships"],
                source=chunk,
            )
            result.append(graph_document)

            newlabels = [node.type for node in graph_document.nodes]
            labels.update(newlabels)

            if self.verbose:
                print(
                    f"Got {len(graph_document.nodes)} nodes and {len(graph_document.relationships)} relationships up till now."
                )

        if self.verbose:
            print("✨ Done!")
            print(f"\nResult ({len(result)}):", result)

        return result

    def _process_with_labels(self, chunk: Document, labels: List[str]) -> BaseMessage:
        """
        Processes the given chunk with the given labels.
        """
        chain = (
            self._extraction_prompt
            | self.llm
            | OutputFixingParser.from_llm(parser=KnowledgeGraphParser(), llm=self.llm)
        )
        output = chain.invoke(
            {"input": generate_prompt_with_labels(chunk.page_content, labels)}
        )
        return output
