# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import pandas as pd
import pathlib
from typing import Optional, Iterator
import time


from azureml.rag.documents import document_chunks_iterator, LazyDocument, StaticDocument, SUPPORTED_EXTENSIONS
from azureml.rag.embeddings import Embeddings
from azureml.rag.utils.azureml import get_secret_from_workspace
from azureml.rag.utils.logging import get_logger, enable_stdout_logging

logger = get_logger('embed')


def create_embeddings(chunks: Iterator[LazyDocument],
                      previous_embeddings: Optional[Embeddings],
                      output: str,
                      embeddings_model: str,
                      batch_size: Optional[int]):

    extra_args = {}
    if batch_size is not None:
        extra_args["batch_size"] = batch_size

    embeddings = previous_embeddings if previous_embeddings is not None else Embeddings.from_uri(embeddings_model, **extra_args)

    pre_embed = time.time()
    embeddings.embed(chunks)
    post_embed = time.time()
    logger.info(f"Embedding took {post_embed - pre_embed} seconds", extra={'print': True})

    embeddings.save(output)


def read_chunks_into_documents(files: Iterator[pathlib.Path]):
    # Append to list of texts and corresponding metadata
    file_max_chunk_len = 0
    for chunk_file in files:
        file_name = chunk_file.name
        logger.info(f'processing chunks for: {file_name}', extra={'print': True})
        chunks_df = pd.read_csv(chunk_file)
        chunks_dict = chunks_df.to_dict()
        max_chunk_len = 0
        for chunk_idx, chunk in chunks_dict["Chunk"].items():
            metadata = chunks_dict["Metadata"][chunk_idx]
            metadata_dict = json.loads(metadata)
            max_chunk_len = max(max_chunk_len, len(chunk))
            yield StaticDocument(metadata_dict['source']['filename'] + str(chunk_idx), chunk, metadata_dict, metadata_dict['source'].get('mtime'))
        logger.info(f'processed {len(chunks_dict["Chunk"])} chunks from {file_name}, max_chunk_len = {max_chunk_len}', extra={'print': True})
        file_max_chunk_len = max(file_max_chunk_len, max_chunk_len)
    logger.info(f'longest chunk seen was {file_max_chunk_len}', extra={'print': True})


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    # If chunking done inline
    parser.add_argument("--documents_source", required=False, type=str)
    parser.add_argument("--source_glob",
                        type=str, default="**/*")
    parser.add_argument("--allowed_extensions", type=str, default=",".join(SUPPORTED_EXTENSIONS))
    parser.add_argument("--documents_source_base_url", type=str, default="")
    parser.add_argument("--document_path_replacement_regex", type=str, required=False)
    parser.add_argument("--chunk_size", type=int, default=512)
    parser.add_argument("--chunk_overlap", type=int, default=None)
    # If chunking was done separately
    parser.add_argument("--chunks_source", required=False, type=str)
    # If adding to previously generated Embeddings
    parser.add_argument("--previous_embeddings", required=False, type=str, default=None)
    parser.add_argument("--output", type=str)
    # Embeddings settings
    parser.add_argument("--embeddings_model", type=str, default="text-embedding-ada-002")
    parser.add_argument("--batch_size", type=int, default=1)
    args = parser.parse_args()

    print('\n'.join(f'{k}={v}' for k, v in vars(args).items()))

    enable_stdout_logging()

    os.environ["OPENAI_API_KEY"] = get_secret_from_workspace("OPENAI-API-KEY")

    if args.chunks_source and args.documents_source:
        raise ValueError("Cannot specify both --chunks_source and --documents_source")
    elif args.chunks_source is None and args.documents_source is None:
        raise ValueError("Must specify either --chunks_source or --documents_source")

    splitter_args = {
        "chunk_size": args.chunk_size,
    }
    if args.chunk_overlap:
        splitter_args['chunk_overlap'] = args.chunk_overlap

    # Mount previous embeddings if given
    previous_embeddings = None
    if args.previous_embeddings is not None:
        from azureml.dataprep.fuse.dprepfuse import MountOptions, rslex_uri_volume_mount
        mnt_options = MountOptions(
            default_permission=0o555, allow_other=False, read_only=True)
        try:
            with rslex_uri_volume_mount(args.previous_embeddings, f'{os.getcwd()}/previous_embeddings', options=mnt_options) as mount_context:
                previous_embeddings_dir_name = None
                # list all folders in previous_embeddings_container_path and find the latest one
                try:
                    previous_embeddings_dir_name = str(max([dir for dir in pathlib.Path(
                        mount_context.mount_point).glob('*') if dir.is_dir() and dir.name != os.environ['AZUREML_RUN_ID']], key=os.path.getmtime).name)
                except Exception as e:
                    logger.warning(
                        f'failed to get latest folder from {mount_context.mount_point} with {e}.', extra={'print': True})
                    pass

                if previous_embeddings_dir_name is not None:
                    logger.info(
                        f'loading from previous embeddings from {previous_embeddings_dir_name} in {mount_context.mount_point}', extra={'print': True})
                    try:
                        previous_embeddings = Embeddings.load(
                            previous_embeddings_dir_name, mount_context.mount_point)
                    except Exception as e:
                        logger.warn(
                            f'Failed to load from previous embeddings with {e}.\nCreating new Embeddings.', extra={'print': True})
        except Exception as e:
            logger.warning(f'Failed to load previous embeddings from mount with {e}, proceeding to create new embeddings.', extra={'print': True})

    # Load chunks to embed
    if args.documents_source is not None:
        logger.info("Getting chunks from documents_source", extra={'print': True})
        per_document_chunks = document_chunks_iterator(args.documents_source, args.source_glob, args.allowed_extensions, args.documents_source_base_url, args.document_path_replacement_regex, splitter_args)

        def flatten_iterator(iterable):
            for i in iterable:
                for j in i:
                    yield j

        chunks = flatten_iterator(per_document_chunks)
    elif args.chunks_source is not None:
        logger.info("Reading chunks from the chunks_source", extra={'print': True})

        files = pathlib.Path(args.chunks_source).rglob("**/*")

        chunks = read_chunks_into_documents(files)
    else:
        raise ValueError("Must specify either --chunks_source or --documents_source")

    create_embeddings(chunks,
                      previous_embeddings,
                      args.output,
                      args.embeddings_model,
                      args.batch_size)
