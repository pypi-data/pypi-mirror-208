# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Embeddings generation and management tools."""
import copy
import datetime
import gzip
import json
import mlflow
import os
import pathlib
import uuid

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator, List, Optional, Union, Tuple

import cloudpickle
from collections import OrderedDict
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings.base import Embeddings as Embedder
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import time
import yaml

from azureml.rag.documents import LazyDocument
from azureml.rag.models import parse_model_uri
from azureml.rag.utils.azureml import get_workspace_from_environment
from azureml.rag.utils.connections import get_connection_credential, get_connection_by_id_v2, workspace_connection_to_credential
from azureml.rag.utils.logging import get_logger


logger = get_logger(__name__)


def _parse_open_ai_args(arguments: dict):
    from langchain.embeddings.openai import OpenAIEmbeddings
    import openai

    logger.info('OpenAI arguments: \n')
    logger.info('\n'.join(f'{k}={v}' for k, v in arguments.items()))

    if "api_type" in arguments:
        openai.api_type = arguments["api_type"]

    if openai.api_type == "azure":
        openai.api_version = arguments.get("api_version", "2023-03-15-preview")

    if "endpoint" in arguments:
        openai.api_base = arguments["endpoint"]

    if "api_base" in arguments:
        openai.api_base = arguments["api_base"]

    if "connection_type" not in arguments:
        openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        if arguments["connection_type"] == "workspace_connection":
            connection_id = arguments.get('connection', {}).get('id', '')
            connection = get_connection_by_id_v2(connection_id)
            openai.api_base = connection.get('properties', {}).get('target')
            openai.api_version = connection.get('properties', {}).get('metadata', {}).get('apiVersion', '2023-03-15-preview')
            credential = workspace_connection_to_credential(connection)
        else:
            credential = get_connection_credential(arguments)
        if hasattr(credential, 'key'):
            openai.api_key = credential.key
        else:
            # Add hack to check for "BAKER-OPENAI-API-KEY"
            if arguments.get("connection_type", "workspace_keyvault") == "workspace_keyvault":
                new_args = copy.deepcopy(arguments)
                new_args["connection"]["key"] = "BAKER-OPENAI-API-KEY"
                credential = get_connection_credential(new_args)
                if hasattr(credential, 'key'):
                    openai.api_key = credential.key
                else:
                    openai.api_key = credential.get_token('https://cognitiveservices.azure.com/.default').token

    embedder = OpenAIEmbeddings(
        openai_api_key=openai.api_key,
        max_retries=100,
    )

    if "model_name" in arguments:
        embedder.model = arguments["model_name"]

    if "model" in arguments:
        embedder.model = arguments["model"]

    # Embeddings endpoint for AOAI uses deployment name and no model name.
    if 'deployment' in arguments and hasattr(embedder, 'deployment'):
        embedder.deployment = arguments["deployment"]

    if "batch_size" in arguments:
        embedder.chunk_size = int(arguments["batch_size"])

    if "embedding_ctx_length" in arguments:
        embedder.embedding_ctx_length = arguments["embedding_ctx_length"]

    return embedder


def get_langchain_embeddings(embedding_kind: str, arguments: dict) -> Embedder:
    """Get an instance of Embedder from the given arguments."""
    if "open_ai" in embedding_kind:
        return _parse_open_ai_args(arguments)
    elif embedding_kind == "hugging_face":
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings

        args = copy.deepcopy(arguments)

        if "model_name" in arguments:
            model_name = arguments["model_name"]
            del args["model_name"]
        elif "model" in arguments:
            model_name = arguments["model"]
            del args["model"]
        else:
            raise ValueError("HuggingFace embeddings require a model name.")

        return HuggingFaceEmbeddings(model_name=model_name)
    elif embedding_kind == "none":
        class NoneEmbeddings(Embedder):
            def embed_documents(self, documents: List[str]) -> List[List[float]]:
                return [[]] * len(documents)

            def embed_query(self, query: str) -> List[float]:
                return []

        return NoneEmbeddings()
    elif embedding_kind == "custom":
        raise NotImplementedError("Custom embeddings are not supported yet.")


def get_embed_fn(embedding_kind: str, arguments: dict) -> Callable[[List[str]], List[List[float]]]:
    """Get an embedding function from the given arguments."""
    if "open_ai" in embedding_kind:
        embedder = _parse_open_ai_args(arguments)

        def embed(texts: List[str]) -> List[List[float]]:
            # AOAI doesn't allow batch_size > 1 so we serialize embedding here to improve error handling
            embeddings = []
            for i in range(0, len(texts), embedder.chunk_size):
                texts_chunk = texts[i:i + embedder.chunk_size]
                try:
                    embeddings.extend(embedder.embed_documents(texts_chunk))
                except Exception as e:
                    logger.error(f'Failed to embed:\n{e}.', exc_info=e, extra={'print': True})
                    print(f'Failed texts: {texts_chunk}\nlengths: {[len(t) for t in texts_chunk]}\n')
                    raise e
            return embeddings

        return embed
    elif embedding_kind == "hugging_face":
        embedder = get_langchain_embeddings(embedding_kind, arguments)

        return embedder.embed_documents
    elif embedding_kind == "custom":
        def load_pickled_function(pickled_embedding_fn):
            import cloudpickle
            return cloudpickle.loads(gzip.decompress(pickled_embedding_fn))

        return arguments.get("embedding_fn", None) or load_pickled_function(arguments.get("pickled_embedding_fn"))
    elif embedding_kind == "none":
        return lambda x: [[]] * len(x)
    else:
        raise ValueError(f"Invalid embeddings kind: {embedding_kind}")


def get_query_embed_fn(embedding_kind: str, arguments: dict) -> Callable[[str], List[float]]:
    """Get an embedding function from the given arguments."""
    if embedding_kind == "open_ai":
        embedder = _parse_open_ai_args(arguments)
        return embedder.embed_query
    elif embedding_kind == "hugging_face":
        embedder = get_langchain_embeddings(embedding_kind, arguments)

        return embedder.embed_query
    elif embedding_kind == "custom":
        def load_pickled_function(pickled_embedding_fn):
            import cloudpickle
            return cloudpickle.loads(gzip.decompress(pickled_embedding_fn))

        return arguments.get("embedding_fn", None) or load_pickled_function(arguments.get("pickled_embedding_fn"))
    elif embedding_kind == "none":
        return lambda x: []
    else:
        raise ValueError("Invalid embeddings kind.")


class EmbeddedDocument(ABC):
    """A document with an embedding."""
    document_id: str
    mtime: Any
    document_hash: str
    metadata: dict

    def __init__(self, document_id: str, mtime, document_hash: str, metadata: dict):
        """Initialize the document."""
        self.document_id = document_id
        self.mtime = mtime
        self.document_hash = document_hash
        self.metadata = metadata

    @abstractmethod
    def get_data() -> str:
        """Get the data of the document."""
        pass

    @abstractmethod
    def get_embeddings() -> List[float]:
        """Get the embeddings of the document."""
        pass


class DataEmbeddedDocument(EmbeddedDocument):
    """A document with an embedding and data."""

    def __init__(self, document_id: str, mtime, document_hash: str, data: str, embeddings: List[float], metadata: dict):
        """Initialize the document."""
        super().__init__(document_id, mtime, document_hash, metadata)
        self._data = data
        self._embeddings = embeddings

    def get_data(self) -> str:
        """Get the data of the document."""
        return self._data

    def get_embeddings(self) -> List[float]:
        """Get the embeddings of the document."""
        return self._embeddings


class ReferenceEmbeddedDocument(EmbeddedDocument):
    """A document with an embedding and a reference to the data."""
    _last_opened_embeddings: Optional[Tuple[str, object]] = None

    def __init__(self, document_id: str, mtime, document_hash: str, path_to_data: str, index, embeddings_container_path: str, metadata: dict):
        """Initialize the document."""
        super().__init__(document_id, mtime, document_hash, metadata)
        self.path_to_data = path_to_data
        self.embeddings_container_path = embeddings_container_path
        self.index = index

    def get_data(self) -> str:
        """Get the data of the document."""
        table = self.open_embedding_file(os.path.join(self.embeddings_container_path, self.path_to_data))
        return table.column('data')[self.index].as_py()

    def get_embeddings(self) -> str:
        """Get the embeddings of the document."""
        table = self.open_embedding_file(os.path.join(self.embeddings_container_path, self.path_to_data))
        return table.column('embeddings')[self.index].as_py()

    @classmethod
    def open_embedding_file(cls, path) -> pa.Table:
        """Open the embedding file and cache it."""
        if cls._last_opened_embeddings is None or cls._last_opened_embeddings[0] != path:
            logger.debug(f'caching embeddings file: \n{path}\n   previous path cached was: \n{cls._last_opened_embeddings}')
            table = pq.read_table(path)
            cls._last_opened_embeddings = (path, table)

        return cls._last_opened_embeddings[1]


class LangChainDocument(LazyDocument):
    """A document with an embedding and a reference to the data."""
    document: Document

    def __init__(self, document: Document):
        """Initialize the document."""
        super().__init__(str(uuid.uuid4()))
        self.document = document

    def modified_time(self) -> Any:
        """Get the modified time of the document."""
        self.document.metadata.get("mtime", None)

    def load_data(self) -> str:
        """Load the data of the document."""
        return self.document.page_content

    def get_metadata(self) -> dict:
        """Get the metadata of the document."""
        return self.document.metadata


class Embeddings:
    """A class for generating embeddings."""
    _embeddings_schema = ["doc_id", "mtime", "hash", "metadata", "path_to_data", "index", "is_local"]
    _data_schema = ["data", "embeddings"]
    _model_context_lengths = {
        "text-embedding-ada-002": 2047
    }
    kind: str
    arguments: dict
    _embed_fn: Callable[[List[str]], List[List[float]]]

    _document_embeddings: OrderedDict

    def __init__(self, kind: str, **kwargs):
        """Initialize the embeddings."""
        self.kind = kind
        self.arguments = kwargs
        self._embed_fn = get_embed_fn(kind, kwargs)
        self._document_embeddings = OrderedDict()
        self.dimension = kwargs.get('dimension', None)

    @staticmethod
    def from_uri(uri: str, **kwargs) -> 'Embeddings':
        """Create an embeddings object from a URI."""
        config = parse_model_uri(uri, **kwargs)
        return Embeddings(**{**config, **kwargs})

    def get_metadata(self):
        """Get the metadata of the embeddings."""
        if self.kind == "custom":
            arguments = copy.deepcopy(self.arguments)
            arguments["pickled_embedding_fn"] = gzip.compress(
                cloudpickle.dumps(arguments["embedding_fn"]))
            del arguments["embedding_fn"]
        else:
            arguments = self.arguments

        metadata = {
            "schema_version": "2",
            "kind": self.kind,
            "dimension": self.get_embedding_dimensions(),
            **self.arguments
        }

        return metadata

    @staticmethod
    def from_metadata(metadata: dict) -> 'Embeddings':
        """Create an embeddings object from metadata."""
        schema_version = metadata.get('schema_version', "1")
        if schema_version == "1":
            embeddings = Embeddings(metadata['kind'], **metadata['arguments'])
            return embeddings
        elif schema_version == "2":
            kind = metadata['kind']
            del metadata['kind']
            if kind == "custom":
                metadata['embedding_fn'] = cloudpickle.loads(
                    gzip.decompress(metadata['pickled_embedding_fn']))
                del metadata['pickled_embedding_fn']

            embeddings = Embeddings(kind, **metadata)
            return embeddings
        else:
            raise ValueError(f"Schema version {schema_version} is not supported")

    @staticmethod
    def load(dir_name: str, embeddings_container_path, metadata_only=False):
        """Load embeddings from a directory."""

        path = os.path.join(embeddings_container_path, dir_name)
        logger.info(f'loading embeddings from : {path}')
        with open(f"{path}/embeddings_metadata.yaml", "r") as f:
            metadata = yaml.safe_load(f)

        if metadata is None:
            raise ValueError("Metadata file is empty.")

        embeddings = Embeddings.from_metadata(metadata)
        if not metadata_only:
            embedding_partitions_files = list(pathlib.Path(path).glob('embeddings*.parquet'))
            logger.info(f'found following embedding partitions: {embedding_partitions_files}')
            for partition in embedding_partitions_files:
                logger.info(f'processing partition: {partition}')
                table = pq.read_table(partition)
                for column in Embeddings._embeddings_schema:
                    if column not in table.column_names:
                        raise ValueError(f'Format of provided embedding file ({partition}) is not supported.  Missing column {column}')
                # TODO: Keep pyarrow partition in Embeddings instance and give out `ReferenceEmbeddedDocument` when iterated over/indexed into with doc_id.
                # Allows each partition of embeddings to be stored in one array and users to retrieve it as one array with cow properties.
                for i in range(table.num_rows):
                    doc_id = table.column('doc_id')[i].as_py()
                    mtime = table.column('mtime')[i].as_py()
                    document_hash = table.column('hash')[i].as_py()
                    metadata = json.loads(table.column('metadata')[i].as_py())
                    path_to_data = None
                    # when loading from previous location convert all its local data references to remote ones
                    if table.column('is_local')[i].as_py():
                        path_to_data = os.path.join(
                            dir_name, table.column('path_to_data')[i].as_py())
                    else:
                        path_to_data = table.column('path_to_data')[i].as_py()
                    index_of_data = table.column('index')[i].as_py()
                    embeddings._document_embeddings[doc_id] = \
                        ReferenceEmbeddedDocument(
                            doc_id, mtime, document_hash, path_to_data, index_of_data, embeddings_container_path, metadata)

                logger.info(f'Loaded {table.num_rows} documents from {partition}')

            logger.info(f'Loaded {len(embeddings._document_embeddings.keys())} documents from {len(embedding_partitions_files)} partitions')

        return embeddings

    def save(self, path: str, with_metadata=True, suffix: Optional[str] = None):
        """Save the embeddings to a directory."""
        doc_ids = []
        mtimes = []
        hashes = []
        paths = []
        indexes = []
        embeddings = []
        local_data = []
        is_local = []
        metadata = []

        local_data_file_name = f'data_{suffix}.parquet' if suffix is not None else 'data.parquet'
        embeddings_file_name = f'embeddings_{suffix}.parquet' if suffix is not None else 'embeddings.parquet'

        for (doc_id, document) in self._document_embeddings.items():
            doc_ids.append(str(doc_id))
            mtimes.append(document.mtime)
            hashes.append(document.document_hash)
            metadata.append(json.dumps(document.metadata))
            if isinstance(document, DataEmbeddedDocument):
                indexes.append(len(local_data))
                local_data.append(document.get_data())
                embeddings.append(document.get_embeddings())
                paths.append(local_data_file_name)
                is_local.append(True)
            elif isinstance(document, ReferenceEmbeddedDocument):
                indexes.append(document.index)
                paths.append(document.path_to_data)
                is_local.append(False)

        import os
        os.makedirs(path, exist_ok=True)

        # write embeddings.parquet
        table = pa.Table.from_arrays(
            [
                pa.array(doc_ids),
                pa.array(mtimes),
                pa.array(hashes),
                pa.array(metadata),
                pa.array(paths),
                pa.array(indexes),
                pa.array(is_local)
            ], names=Embeddings._embeddings_schema)
        pq.write_table(table, os.path.join(path, embeddings_file_name))

        # write data.paruet with data embedded in this run
        data_table = pa.Table.from_arrays(
            [
                pa.array(local_data),
                pa.array(embeddings)
            ], names=["data", "embeddings"])
        pq.write_table(data_table, os.path.join(path, local_data_file_name))

        # write metadata file
        if with_metadata:
            self.save_metadata(path)

    def save_metadata(self, path):
        """Save the metadata to a directory."""
        with open(f"{path}/embeddings_metadata.yaml", "w+") as f:
            yaml.dump(self.get_metadata(), f)

    def get_query_embed_fn(self) -> Callable[[str], List[float]]:
        """Returns a function that embeds a query string."""
        return get_query_embed_fn(self.kind, self.arguments)

    def get_embedding_dimensions(self) -> Optional[int]:
        """Returns the embedding dimensions."""
        if self.dimension is not None:
            return self.dimension
        elif len(self._document_embeddings) > 0:
            return len(next(iter(self._document_embeddings.values())).get_embeddings())
        else:
            return None

    def as_langchain_embeddings(self) -> Embedder:
        """Returns a langchain Embedder that can be used to embed text."""
        return get_langchain_embeddings(self.kind, self.arguments)

    # TODO: Either we need to implement the same split/embed/average flow used by `_get_len_safe_embeddings`
    # on OpenAIEmbeddings or make sure that data_chunking_component always respects max chunk_size.
    # Short term fix is to truncate any text longer than the embedding_ctx_limit if it's set.
    def get_embedding_ctx_length_truncate_func(self):
        """Returns a function that truncates text to the embedding context length if it's set."""
        model = ''
        if 'model' in self.arguments:
            model = self.arguments['model']
        elif 'model_name' in self.arguments:
            model = self.arguments['model_name']

        ctx_length = Embeddings._model_context_lengths.get(model, None)

        if ctx_length:
            import tiktoken

            def truncate_by_tokens(text):
                enc = tiktoken.encoding_for_model(model)
                # Some chunks still managed to tokenize above the limit so leaving 20 tokens buffer.
                tokens = enc.encode(text=text)[:ctx_length - 20]
                return enc.decode(tokens)
            return truncate_by_tokens
        else:
            return lambda text: text

    def embed(self, input_documents: Union[Iterator[LazyDocument], BaseLoader]):
        """
        Embeds inout documents if they are new or changed and mutates current instance to drop embeddings for documents that are no longer present.
        """
        self._document_embeddings = self._get_embeddings_internal(input_documents)

    def embed_and_create_new_instance(self, input_documents: Union[Iterator[LazyDocument], BaseLoader]) -> 'Embeddings':
        """
        Embeds input documents if they are new or changed and returns a new instance with the new embeddings. Current instance is not mutated.
        """
        document_embeddings = self._get_embeddings_internal(input_documents)
        new_embeddings = Embeddings(self.kind, **self.arguments)
        new_embeddings._document_embeddings = document_embeddings
        return new_embeddings

    def _get_embeddings_internal(self, input_documents: Union[Iterator[LazyDocument], BaseLoader]) -> OrderedDict:
        if self._embed_fn is None:
            raise ValueError("No embed function provided.")

        if isinstance(input_documents, BaseLoader):
            input_documents = iter([LangChainDocument(d)
                                   for d in input_documents.load()])

        documents_to_embed = []
        documents_embedded = OrderedDict()
        for document in input_documents:
            logger.info(f'Processing document: {document.document_id}')
            mtime = document.modified_time()
            current_embedded_document = self._document_embeddings.get(
                document.document_id)
            if mtime \
                    and current_embedded_document \
                    and current_embedded_document.mtime \
                    and current_embedded_document.mtime == mtime:
                documents_embedded[document.document_id] = current_embedded_document

                try:
                    mtime = datetime.datetime.fromtimestamp(mtime)
                except Exception:
                    pass
                logger.info(
                    f'Skip embedding document {document.document_id} as it has not been modified since last embedded at {mtime}')
                continue

            import hashlib
            document_data = document.load_data()
            document_hash = hashlib.sha256(
                document_data.encode('utf-8')).hexdigest()

            if current_embedded_document and current_embedded_document.document_hash == document_hash:
                documents_embedded[document.document_id] = current_embedded_document
                logger.info(
                    f'Skip embedding document {document.document_id} as it has not been modified since last embedded')
                continue

            document_metadata = document.get_metadata()
            documents_to_embed.append(
                (document.document_id, mtime, document_data, document_hash, document_metadata))

        logger.info(f'Documents to embed: {len(documents_to_embed)}'
                    f'\nDocuments reused: {len(documents_embedded.keys())}')
        mlflow.log_metrics({
            'Embedded Documents': len(documents_to_embed),
            'Reused Documents': len(documents_embedded.keys())
        })

        truncate_func = self.get_embedding_ctx_length_truncate_func()

        data_to_embed = [truncate_func(t) for (_, _, t, _, _) in documents_to_embed]

        embeddings = []
        try:
            embeddings = self._embed_fn(data_to_embed)
        except Exception as e:
            logger.error(f'Failed to get embeddings with error: {e}')
            raise

        for ((doc_id, mtime, document_data, document_hash, document_metadata), embeddings) in zip(documents_to_embed, embeddings):
            documents_embedded[doc_id] = \
                DataEmbeddedDocument(doc_id, mtime, document_hash,
                                     document_data, embeddings, document_metadata)

        return documents_embedded

    def as_faiss_index(self):
        """Returns a FAISS index that can be used to query the embeddings."""""
        from langchain.docstore.in_memory import InMemoryDocstore
        from langchain.vectorstores import FAISS
        from langchain.vectorstores.faiss import dependable_faiss_import
        import numpy as np

        logger.info("Building index", extra={'print': True})
        t1 = time.time()
        num_source_docs = 0
        documents = []
        embeddings = []
        for doc_id, emb_doc in self._document_embeddings.items():
            logger.info(f'Adding document: {doc_id}', extra={'print': True})
            logger.debug(f'{doc_id},{emb_doc.document_hash},{emb_doc.get_embeddings()[0:20]}', extra={'print': True})
            embeddings.append(emb_doc.get_embeddings())
            # TODO: LazyDocument/RefDocument gets uri to page_content
            documents.append(
                Document(
                    page_content=emb_doc.get_data(),
                    metadata={
                        "source_doc_id": doc_id,
                        "chunk_hash": emb_doc.document_hash,
                        "mtime": emb_doc.mtime,
                        **emb_doc.metadata
                    }
                )
            )
            num_source_docs += 1

        index_to_id = {i: doc.metadata["source_doc_id"] for i, doc in enumerate(documents)}
        docstore = InMemoryDocstore(
            {index_to_id[i]: doc for i, doc in enumerate(documents)}
        )

        faiss = dependable_faiss_import()
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings, dtype=np.float32))

        logger.info(f"Built index from {num_source_docs} documents and {len(embeddings)} chunks, took {time.time()-t1:.4f} seconds", extra={'print': True})

        return FAISS(self.get_query_embed_fn(), index, docstore, index_to_id)

    def write_as_faiss_mlindex(self, output_path: Path):
        """Writes the embeddings to a FAISS MLIndex file."""
        faiss_index = self.as_faiss_index()

        logger.info("Saving index", extra={'print': True})
        faiss_index.save_local(str(output_path))

        mlindex_config = {
            "embeddings": self.get_metadata()
        }
        mlindex_config["index"] = {
            "kind": "faiss",
            "engine": "langchain.vectorstores.FAISS",
            "method": "FlatL2"
        }
        with open(output_path / "MLIndex", "w") as f:
            yaml.dump(mlindex_config, f)
