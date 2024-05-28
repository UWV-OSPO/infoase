from abc import ABC
from typing import List, Optional, Any

import chromadb
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Chroma


class CachedChroma(Chroma, ABC):
    """
    Wrapper around Chroma to make caching embeddings easier.

    It automatically uses a cached version of a specified collection, if available.

        Example:
            .. code-block:: python

                    from langchain.vectorstores import Chroma
                    from langchain.embeddings.openai import OpenAIEmbeddings

                    embeddings = OpenAIEmbeddings()
                    vectorstore = CachedChroma.from_documents_with_cache(
                        ".persisted_data", texts, embeddings, collection_name="fun_experiement"
                    )
        """

    @classmethod
    def from_documents_with_cache(
            cls,
            persist_directory: str,
            documents: List[Document],
            embedding: Optional[Embeddings] = None,
            ids: Optional[List[str]] = None,
            collection_name: str = Chroma._LANGCHAIN_DEFAULT_COLLECTION_NAME,
            client_settings: Optional[chromadb.config.Settings] = None,
            **kwargs: Any,
    ) -> Chroma:
        settings = chromadb.config.Settings(
            persist_directory=persist_directory
        )

        client = chromadb.Client(settings)
        collection_names = [c.name for c in client.list_collections()]

        if collection_name in collection_names:
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding,
                persist_directory=persist_directory,
                client_settings=client_settings,
            )

        ## TODO NEVER LOADED FROM CACHE

        return Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            ids=ids,
            collection_name=collection_name,
            persist_directory=persist_directory,
            client_settings=client_settings,
            **kwargs
        )