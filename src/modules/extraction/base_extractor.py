import os
import abc
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_community.graphs.graph_document import GraphDocument
from modules.utils.load_env import load_env

load_env()


class BaseExtractor(abc.ABC):
    @abc.abstractmethod
    def run_list(self, data: List[Document]) -> List[GraphDocument]:
        pass

    @abc.abstractmethod
    def run(self, data: str) -> List[GraphDocument]:
        pass

    def _chunk_text(self, text: str, llm: BaseChatModel, messages) -> List[Document]:
        return self._chunk_documents([Document(page_content=text)], llm, messages)

    def _chunk_documents(
        self, documents: List[Document], llm: BaseChatModel, messages
    ) -> List[Document]:
        if llm is None:
            raise ValueError("Either llm must be provided to calculate chunk size.")

        gpt_max_tokens = int(os.getenv("AZURE_OPENAI_MODEL_MAX_TOKENS", "4096"))

        prompt_tokens = llm.get_num_tokens_from_messages(messages=messages)
        # Reduce by 400 to reserve room for allowed nodes and rels
        chunk_size = gpt_max_tokens - prompt_tokens - 400
        print("🍪 Chunk size", chunk_size)
        print("📕 Documents size", len(documents))

        chunk_overlap = 0
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # Split the documents into chunks that fit the token window.
        splits = text_splitter.split_documents(documents)
        return splits
