import os
import abc
import hashlib
from typing import List
from langchain_community.document_loaders import (
    UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document
from uwv_toolkit.utils import load_env, persistent_path, azure_embeddings
from uwv_toolkit.langchain import CachedChroma


load_env()


class BaseChromaVectorDB(abc.ABC):
    documents: List[str] = None
    persist_dir: str = persistent_path("chroma_db", force_create=False)
    collection_name: str = "default_collection"

    def __init__(
        self,
        collection_name: str = None,
        persist_dir: str = None,
        documents: List[str] = None,
    ):
        """
        Initialize the ChromaDB object.

        Args:
            collection_name (str, optional): The name of the collection.
            persist_dir (str, optional): The directory to persist the ChromaDB. Defaults to None.
            documents (List[str], optional): The documents to use for the ChromaDB. Defaults to None.

        Raises:
            ValueError: If no collection name is provided.
            ValueError: If no documents are provided.
        """
        if collection_name:
            self.collection_name = collection_name

        if self.collection_name is None:
            raise ValueError("Please provide a collection name for the Chroma DB.")

        if persist_dir is not None:
            self.persist_dir = persist_dir
        if documents is not None:
            self.documents = documents

        if self.documents is None:
            raise ValueError("Please provide documents")

    def _load_documents(self) -> List[Document]:
        """
        Method that loads the documents into the vector object

        Returns:
            List[Document]: The list of documents

        Raises:
            ValueError: If no documents are specified
        """

        if len(self.documents) == 0:
            raise ValueError("No documents specified")

        docs = []
        for doc in self.documents:
            # Get the extension of the file
            ext = os.path.splitext(doc)[1]

            # Get the loader for the file based on the extension
            if ext == ".html" or ext == ".htm":
                loader = UnstructuredHTMLLoader(doc)
            elif ext == ".pdf":
                loader = PyPDFLoader(doc)
            elif ext == ".docx":
                loader = UnstructuredWordDocumentLoader(doc)
            else:
                raise ValueError(f"Unknown file extension: {ext}")

            docs.extend(loader.load())

        return docs

    @abc.abstractmethod
    def _split_documents(self, docs: List[Document]):
        """Method that splits the documents into chunks. For example:

        # text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=1000, chunk_overlap=200
        # )
        # splits = text_splitter.split_documents(docs)
        """

    def setup(self):
        """Method to setup the vector object"""

        docs = self._load_documents()
        splits = self._split_documents(docs)

        ids = []
        for index, doc in enumerate(splits):
            ids.append(
                hashlib.sha256(
                    (doc.metadata["source"] + "_" + str(index)).encode()
                ).hexdigest()
            )

        return CachedChroma.from_documents_with_cache(
            documents=splits,
            collection_name=self.collection_name,
            ids=ids,
            embedding=azure_embeddings(),
            persist_directory=self.persist_dir,
        )
