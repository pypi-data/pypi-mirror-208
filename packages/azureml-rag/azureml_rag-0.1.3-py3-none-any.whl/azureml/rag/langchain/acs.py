# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Azure Cognitive Search vector store."""
import base64
import json
from langchain.embeddings.base import Embeddings
from langchain.schema import BaseRetriever, Document
from langchain.vectorstores.base import VectorStore
from pydantic import BaseModel, Extra, root_validator
import requests
import tenacity
from typing import Dict, List, Optional, Iterable, Any, Tuple

from azureml.rag.utils.logging import get_logger


logger = get_logger('langchain.acs')


# TODO: FieldMappings dataclass


@tenacity.retry(
    wait=tenacity.wait_fixed(5),  # wait 5 seconds between retries
    stop=tenacity.stop_after_attempt(3),  # stop after 3 attempts
    reraise=True,  # re-raise the exception after the last retry attempt
)
def send_post_request(url, headers, payload):
    """Send a POST request to the specified URL with the specified headers and payload."""
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    # Raise an exception if the response contains an HTTP error status code
    response.raise_for_status()
    return response


def get_acs_headers(credential) -> dict:
    """Get the headers for Azure Cognitive Search."""
    from azure.identity import DefaultAzureCredential
    from azure.core.credentials import AzureKeyCredential
    headers = {
        "Content-Type": "application/json"
    }
    if isinstance(credential, DefaultAzureCredential):
        headers["Authorization"] = f"Bearer {credential.get_token('https://search.azure.com/.default').token}"
    elif isinstance(credential, AzureKeyCredential):
        headers["api-key"] = credential.key
    return headers


class AzureCognitiveSearchVectorStore(VectorStore):
    """Wrapper around Azure Cognitive Search Index which has embeddings vectors."""

    def __init__(self, endpoint: str, index_name: str, embeddings: Embeddings, field_mapping: dict, credential: Optional[object] = None):
        """Initialize a vector store from an Azure Cognitive Search Index."""
        try:
            from azure.identity import DefaultAzureCredential  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-identity python package. "
                "Please install it with `pip install azure-identity`."
            )
        try:
            from azure.core.credentials import AzureKeyCredential  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-core python package. "
                "Please install it with `pip install azure-core`."
            )
        self.endpoint = endpoint
        self.index_name = index_name
        self.credential = credential if credential is not None else DefaultAzureCredential()
        self.embeddings = embeddings
        self.field_mapping = field_mapping

    @classmethod
    def from_mlindex(cls, uri: str):
        """Create a vector store from a MLIndex uri."""
        from ..mlindex import MLIndex
        mlindex = MLIndex(uri)
        return mlindex.as_langchain_vectorstore()

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        """Search for similar documents by query."""
        return [item[0] for item in self._similarity_search_with_relevance_scores(query, k, **kwargs)]

    def _similarity_search_with_relevance_scores(self, query: str, k: int = 4, **kwargs: Any) -> List[Tuple[Document, float]]:
        """Search for similar documents by query."""
        embedded_query = self.embeddings.embed_query(query)
        return self._similarity_search_by_vector_with_relevance_scores(query, embedded_query, k, **kwargs)

    def _similarity_search_by_vector_with_relevance_scores(self, query: Optional[str], embedded_query: List[float], k: int = 4, **kwargs) -> List[Tuple[Document, float]]:
        post_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-07-01-Preview"
        headers = get_acs_headers(self.credential)
        post_payload = {}

        if query is not None:
            logger.info(f"Query: {query}")
            post_payload["search"] = query

        post_payload["top"] = str(k)

        if self.field_mapping.get('embedding', None) is not None:
            logger.info(f"Using embedding field: {self.field_mapping['embedding']}")
            post_payload["vector"] = {
                "value": embedded_query,
                "fields": self.field_mapping['embedding'],
                "k": k
            }

        response = send_post_request(post_url, headers, post_payload)

        if response.content:
            response_json = response.json()
            logger.info(response_json)
            if 'value' in response_json:
                return [
                    (
                        Document(
                            page_content=item[self.field_mapping['content']],
                            metadata={
                                "id": item["id"],
                                "doc_id": base64.b64decode(item["id"]).decode('utf8'),
                                "content_vector": item[self.field_mapping['embedding']] if self.field_mapping.get('embedding', None) is not None else None,
                                **(json.loads(item[self.field_mapping['metadata']]) if self.field_mapping['metadata'].endswith('json_string') else item[self.field_mapping['metadata']])},
                        ),
                        item['@search.score']
                    )
                    for item in response_json['value']
                ]
            else:
                logger.info('no value in response from ACS')
        else:
            logger.info('empty response from ACS')

        return []

    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        """Add texts to the vector store."""
        raise NotImplementedError

    def similarity_search_by_vector_with_relevance_scores(self, vector: List[float], k: int = 4, **kwargs: Any) -> List[Tuple[Document, float]]:
        """Search for similar documents by vector with relevance scores."""
        if self.field_mapping.get('embedding', None) is None:
            raise ValueError("No embedding field specified in field_mapping")
        return self._similarity_search_by_vector_with_relevance_scores(None, vector, k, **kwargs)

    def similarity_search_by_vector(self, vector: List[float], k: int = 4, **kwargs: Any) -> List[Document]:
        """Search for similar documents by vector."""
        if self.field_mapping.get('embedding', None) is None:
            raise ValueError("No embedding field specified in field_mapping")
        return [doc for (doc, _) in self._similarity_search_by_vector_with_relevance_scores(None, vector, k, **kwargs)]

    @classmethod
    def from_texts(cls, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> VectorStore:
        """Create a vector store from a list of texts."""
        raise NotImplementedError


# TODO: Expose semantic search options
class AzureCognitiveSearchRetriever(BaseRetriever, BaseModel):
    """Retriever class for Azure Cognitive Search."""
    top_k: int = 16
    index_name: str
    endpoint: str
    credential: Optional[object]

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        try:
            from azure.search.documents import SearchClient  # noqa:F401
            from azure.search.documents.indexes import SearchIndexClient  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-search python package. "
                "Please install it with `pip install azure-search`."
            )
        try:
            from azure.identity import DefaultAzureCredential  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-identity python package. "
                "Please install it with `pip install azure-identity`."
            )
        try:
            from azure.core.credentials import AzureKeyCredential  # noqa:F401
        except ImportError:
            raise ValueError(
                "Could not import azure-core python package. "
                "Please install it with `pip install azure-core`."
            )
        return values

    @classmethod
    def from_mlindex(cls, uri: str):
        """Create a retriever from a MLIndex uri."""
        from ..mlindex import MLIndex
        mlindex = MLIndex(uri)
        return mlindex.as_langchain_retriever()

    def get_search_client(self):
        """Get search client."""
        from azure.identity import DefaultAzureCredential
        from azure.search.documents import SearchClient

        credential = self.credential
        if self.credential is None:
            credential = DefaultAzureCredential()

        return SearchClient(endpoint=self.endpoint, index_name=self.index_name, credential=credential)

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents for a query."""
        client = self.get_search_client()

        # if self.embed_query:
        #     query_vector = self.embeddings.embed_query(query)

        results = client.search(search_text=query, top=self.top_k)

        def expand_meta(search_result: dict):
            final_meta = {}
            for k, v in search_result.items():
                # AzureML inserts this key to contain generic metadata
                if k == 'meta_json_string':
                    try:
                        final_meta.update(json.loads(v))
                    except Exception as e:
                        logger.warning(f"Error parsing meta_json_string for doc: '{search_result['id']}': {e}")
                final_meta[k] = v
            return final_meta

        return [
            Document(page_content=result["content"], metadata=expand_meta(result))
            for result in results
        ]

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents for a query."""
        raise NotImplementedError
