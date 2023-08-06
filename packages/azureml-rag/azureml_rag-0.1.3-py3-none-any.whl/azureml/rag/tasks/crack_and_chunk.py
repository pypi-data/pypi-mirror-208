# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import openai
import pandas as pd
from pathlib import Path
import time

from azureml.rag.utils.logging import get_logger, enable_stdout_logging
from azureml.rag.documents import SUPPORTED_EXTENSIONS, DocumentChunksIterator, split_documents, crack_documents
from azureml.rag.models import parse_model_uri
from azureml.rag.utils.azureml import get_secret_from_workspace


logger = get_logger('crack_and_chunk')


def chunks_to_dataframe(chunks) -> pd.DataFrame:
    import json

    metadata = []
    data = []
    for chunk in chunks:
        metadata.append(json.dumps(chunk.get_metadata()))
        data.append(chunk.load_data())
    #(metadata, data) = [(json.dumps(chunk.metadata), chunk.load_data()) for chunk in chunks]
    chunks_dict = {
        "Metadata": metadata,
        "Chunk": data
    }

    return pd.DataFrame(chunks_dict)


def write_chunks_to_csv(chunks_df, output_path):
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    chunks_df.to_csv(output_path, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str)
    parser.add_argument("--input_glob", type=str, default="**/*")
    parser.add_argument("--allowed_extensions", required=False, type=str, default=",".join(SUPPORTED_EXTENSIONS))
    parser.add_argument("--chunk_size", type=int)
    parser.add_argument("--chunk_overlap", type=int)
    parser.add_argument("--output_title_chunk", type=str)
    parser.add_argument("--output_summary_chunk", type=str, default=None)
    parser.add_argument("--data_source_url", type=str, required=False)
    parser.add_argument("--document_path_replacement_regex", type=str, required=False)
    parser.add_argument("--max_sample_files", type=int, default=-1)
    parser.add_argument("--include_summary", type=str, default="False")
    parser.add_argument("--summary_model_config", type=str, default='{"type": "azure_open_ai", "model_name": "gpt-35-turbo", "deployment_name": "gpt-35-turbo"}')
    parser.add_argument("--openai_api_version", type=str, default='2023-03-15-preview')
    parser.add_argument("--openai_api_type", type=str, default=None)
    parser.add_argument("--use_rcts", type=bool, default=False)

    args = parser.parse_args()
    print('\n'.join(f'{k}={v}' for k, v in vars(args).items()))

    enable_stdout_logging()

    # Get all files in directory, recursively
    files = Path(args.input_data).rglob(args.input_glob)

    summary_model_config = None
    include_summary = (args.include_summary == "True" or args.include_summary == "true")
    if include_summary:
        import json

        try:
            summary_model_config = json.loads(args.summary_model_config)
            # TODO: For back compat, remove in a few weeks.
            summary_model_config['kind'] = summary_model_config['type']
            del summary_model_config['type']
            summary_model_config['model'] = summary_model_config['model_name']
            del summary_model_config['model_name']
            if 'deployment_name' in summary_model_config:
                summary_model_config['deployment'] = summary_model_config['deployment_name']
                del summary_model_config['deployment_name']
        except json.decoder.JSONDecodeError:
            # Try parse as uri
            summary_model_config = parse_model_uri(args.summary_model)

        logger.info(f"Using summary_model: {json.dumps(summary_model_config, indent=2)}", extra={'print': True})
        if summary_model_config.get("kind") == "azure_open_ai" or summary_model_config.get("api_type") == "azure":
            summary_model_config["key"] = get_secret_from_workspace("OPENAI-API-KEY")
            summary_model_config["kind"] = "open_ai"
            summary_model_config["api_type"] = "azure"
            summary_model_config["api_version"] = args.openai_api_version
            summary_model_config["api_base"] = summary_model_config.get('endpoint') if summary_model_config.get('endpoint') is not None else get_secret_from_workspace("OPENAI-API-BASE")
            openai.api_version = summary_model_config["api_version"]
            openai.api_type = summary_model_config["api_type"]
            openai.api_base = summary_model_config["api_base"]
            openai.api_key = summary_model_config["key"]

    chunked_documents = DocumentChunksIterator(
        files_source=args.input_data,
        glob=args.input_glob,
        base_url=args.data_source_url,
        document_path_replacement_regex=args.document_path_replacement_regex,
        chunked_document_processors = [lambda docs: split_documents(docs, splitter_args={'chunk_size': args.chunk_size, 'chunk_overlap': args.chunk_overlap, 'use_rcts': args.use_rcts})],
    )
    file_count = 0
    for document in chunked_documents:
        file_count += 1
        logger.info(f'Processing file: {document.source.filename}', extra={'print': True})
        # TODO: Ideally make it easy to limit number of files with a `- take: n` operation on input URI in MLTable
        if (args.max_sample_files != -1 and file_count >= args.max_sample_files):
            logger.info(f"file count: {file_count} - reached max sample file count: {args.max_sample_files}", extra={'print': True})
            break
        write_chunks_to_csv(chunks_to_dataframe(document.chunks), Path(args.output_title_chunk) / f"Chunks_{Path(document.source.filename).name}.csv")
    logger.info(f"Processed {file_count} files", extra={'print': True})

    file_count = 0
    if include_summary:
        chunked_documents = DocumentChunksIterator(
            files_source=args.input_data,
            glob=args.input_glob,
            base_url=args.data_source_url,
            document_path_replacement_regex=args.document_path_replacement_regex,
            source_loader=lambda sources: crack_documents(sources, summary_model_config=summary_model_config),
            chunked_document_processors = [lambda docs: split_documents(docs, splitter_args={'chunk_size': args.chunk_size, 'chunk_overlap': args.chunk_overlap, 'use_rcts': args.use_rcts})]
        )
        total_time = 0
        for document in chunked_documents:
            file_start_time = time.time()
            if (args.max_sample_files != -1 and file_count >= args.max_sample_files):
                logger.info(f"file count: {file_count} - reached max sample file count: {args.max_sample_files}", extra={'print': True})
                break
            write_chunks_to_csv(chunks_to_dataframe(document.chunks), Path(args.output_summary_chunk) / f"Chunks_{Path(document.source.filename).name}.csv")
            file_end_time = time.time()
            file_time = file_end_time - file_start_time
        logger.info(f"Write chunks to {file_count} files in {total_time} seconds (chunk generation time excluded)", extra={'print': True})
