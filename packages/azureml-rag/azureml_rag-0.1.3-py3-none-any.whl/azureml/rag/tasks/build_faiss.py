# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File for building FAISS Indexes."""
import os
from pathlib import Path

from azureml.rag.embeddings import Embeddings
from azureml.rag.utils.logging import get_logger, enable_stdout_logging

logger = get_logger('build_faiss')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--embeddings", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()

    print('\n'.join(f'{k}={v}' for k, v in vars(args).items()))

    enable_stdout_logging()

    raw_embeddings_uri = args.embeddings
    logger.info(f'got embeddings uri as input: {raw_embeddings_uri}', extra={'print': True})
    splits = raw_embeddings_uri.split('/')
    embeddings_dir_name = splits.pop(len(splits)-2)
    logger.info(f'extracted embeddings directory name: {embeddings_dir_name}', extra={'print': True})
    parent = '/'.join(splits)
    logger.info(f'extracted embeddings container path: {parent}', extra={'print': True})

    # Mock OPENAI_API_KEY being set so that loading Embeddings doesn't fail, we don't need to do any embedding so should be fine
    os.environ['OPENAI_API_KEY'] = 'nope'

    from azureml.dataprep.fuse.dprepfuse import (MountOptions, rslex_uri_volume_mount)
    mnt_options = MountOptions(
        default_permission=0o555, allow_other=False, read_only=True)
    logger.info(f'mounting embeddings container from: \n{parent} \n   to: \n{os.getcwd()}/raw_embeddings', extra={'print': True})
    with rslex_uri_volume_mount(parent, f'{os.getcwd()}/raw_embeddings', options=mnt_options) as mount_context:
        logger.info("Loading Embeddings", extra={'print': True})
        emb = Embeddings.load(embeddings_dir_name, mount_context.mount_point)

        emb.write_as_faiss_mlindex(Path(args.output))

    logger.info('Generated FAISS index', extra={'print': True})
