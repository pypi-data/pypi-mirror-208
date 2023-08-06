# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex class for interacting with MLIndex assets."""
from azureml.rag.embeddings import Embeddings
from azureml.rag.utils.connections import get_connection_credential
from azureml.rag.utils.logging import get_logger
import tempfile
from typing import Union


logger = get_logger('mlindex')


class MLIndex:
    """MLIndex class for interacting with MLIndex assets."""
    base_uri: str
    index_config: dict
    embeddings_config: dict

    def __init__(self, uri: Union[str, object]):
        """Initialize MLIndex from a URI or AzureML Data Asset"""
        if isinstance(uri, str):
            uri = str(uri)
        else:
            # Assume given AzureML Data Asset
            uri = uri.path
        import yaml
        try:
            import fsspec
        except ImportError:
            raise ValueError(
                "Could not import fsspec python package. "
                "Please install it with `pip install fsspec`."
            )
        try:
            import azureml.fsspec
        except ImportError:
            raise ValueError(
                "Could not import azureml-fsspec python package. "
                "Please install it with `pip install azureml-fsspec`."
            )

        self.base_uri = uri

        mlindex_yaml = None
        try:
            mlindex_file = fsspec.open(f"{uri.rstrip('/')}/MLIndex", 'r')
            # parse yaml to dict
            with mlindex_file as f:
                mlindex_yaml = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Could not find MLIndex: {e}") from e

        self.index_config = mlindex_yaml.get('index', {})
        if self.index_config is None:
            raise ValueError("Could not find index config in MLIndex yaml")
        self.embeddings_config = mlindex_yaml.get('embeddings', {})
        if self.embeddings_config is None:
            raise ValueError("Could not find embeddings config in MLIndex yaml")

    def get_langchain_embeddings(self):
        """Get the LangChainEmbeddings from the MLIndex"""
        embeddings = Embeddings.from_metadata(self.embeddings_config)

        return embeddings.as_langchain_embeddings()

    def as_langchain_vectorstore(self):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        index_kind = self.index_config.get('kind', None)
        if index_kind == 'acs':
            from azureml.rag.langchain.acs import AzureCognitiveSearchVectorStore

            credential = get_connection_credential(self.index_config)

            return AzureCognitiveSearchVectorStore(
                index_name=self.index_config.get('index'),
                endpoint=self.index_config.get('endpoint'),
                embeddings=self.get_langchain_embeddings(),
                field_mapping=self.index_config.get('field_mapping', {}),
                credential=credential,
            )
        elif index_kind == 'faiss':
            from fsspec.core import url_to_fs
            from langchain.vectorstores.faiss import FAISS

            embeddings = Embeddings.from_metadata(self.embeddings_config).as_langchain_embeddings()

            fs, uri = url_to_fs(self.base_uri)

            with tempfile.TemporaryDirectory() as tmpdir:
                fs.download(f"{uri.rstrip('/')}/index.pkl", f"{str(tmpdir)}")
                fs.download(f"{uri.rstrip('/')}/index.faiss", f"{str(tmpdir)}")
                langchain_faiss = FAISS.load_local(str(tmpdir), embeddings)

            return langchain_faiss
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def as_langchain_retriever(self, **kwargs):
        """Converts MLIndex to a retriever object that can be used with langchain, may download files."""
        index_kind = self.index_config.get('kind', None)
        if index_kind == 'acs':
            return self.as_langchain_vectorstore().as_retriever(**kwargs)
            # from azureml.rag.langchain.acs import AzureCognitiveSearchRetriever

            # credential = get_connection_credential(self.index_config)

            # return AzureCognitiveSearchRetriever(
            #     index_name=self.index_config.get('index'),
            #     endpoint=self.index_config.get('endpoint'),
            #     credential=credential,
            #     top_k=self.index_config.get('top_k', 4),
            # )
        elif index_kind == 'faiss':
            return self.as_langchain_vectorstore().as_retriever()
        else:
            raise ValueError(f"Unknown index kind: {index_kind}")

    def __repr__(self):
        """Returns a string representation of the MLIndex object."""
        return f"MLIndex(index_config={self.index_config}, embeddings_config={self.embeddings_config})"
