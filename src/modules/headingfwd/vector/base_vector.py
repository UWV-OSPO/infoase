import bs4
import os
import hashlib
from typing import List
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
)
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from modules.utils import Utilities
from modules.utils.load_env import load_env

load_env()


class BaseVector:
    documents: List[str] = []
    persist_dir: str = f"{Utilities.persistent_storage_path()}/vectordb"
    _chunk_size: int = 1000
    _chunk_overlap: int = 200
    _enable_cache: bool = False

    def __init__(
        self,
        persist_dir: str = None,
        documents: List[str] = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        enable_cache: bool = False,
    ):
        if chunk_size is not None:
            self._chunk_size = chunk_size
        if chunk_overlap is not None:
            self._chunk_overlap = chunk_overlap
        if persist_dir is not None:
            self.persist_dir = persist_dir
        if documents is not None:
            self.documents = documents
        self._enable_cache = enable_cache

    def load_from_cache(
        self,
        persist_dir: str = None,
        force_setup: bool = False,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ) -> Chroma:
        """TODO: improve checking if db exists"""

        if chunk_size is not None:
            self._chunk_size = chunk_size
        if chunk_overlap is not None:
            self._chunk_overlap = chunk_overlap
        if persist_dir is None:
            persist_dir = self.persist_dir

        if not os.path.exists(persist_dir):
            if force_setup:
                return self.setup()
            return None

        return Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings(),
        )

    def embeddings(self):

        azure_embeddings = AzureOpenAIEmbeddings(
            openai_api_key=os.environ["EMBEDDINGS_AZURE_OPENAI_API_KEY"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=os.environ["EMBEDDINGS_AZURE_OPENAI_ENDPOINT"],
            deployment=os.environ["EMBEDDINGS_AZURE_OPENAI_DEPLOYMENT"],
        )
        if self._enable_cache:
            store = LocalFileStore(f"{self.persist_dir}/embeddings_cache/")

            return CacheBackedEmbeddings.from_bytes_store(
                azure_embeddings, store, namespace=azure_embeddings.model
            )
        else:
            return azure_embeddings

        return embeddings
        # return HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

    def setup(self):
        """Method to setup the vector object"""

        if len(self.documents) == 0:
            raise ValueError("No documents specified")

        docs = []
        for doc in self.documents:
            # Get the extension of the file
            ext = os.path.splitext(doc)[1]

            # Get the loader for the file based on the extension
            if ext == ".html":
                loader = UnstructuredHTMLLoader(doc)
            elif ext == ".pdf":
                loader = PyPDFLoader(doc)
            elif ext == ".docx":
                loader = UnstructuredWordDocumentLoader(doc)
            else:
                raise ValueError(f"Unknown file extension: {ext}")

            docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(docs)

        ids = []
        for index, doc in enumerate(chunks):
            ids.append(
                hashlib.sha256(
                    (doc.metadata["source"] + "_" + str(index)).encode()
                ).hexdigest()
            )

        return Chroma.from_documents(
            chunks,
            self.embeddings(),
            persist_directory=self.persist_dir,
            ids=ids,
        )
