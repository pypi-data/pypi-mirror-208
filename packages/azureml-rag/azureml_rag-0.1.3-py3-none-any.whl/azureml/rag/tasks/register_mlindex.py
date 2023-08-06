# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File for registering ML Indexes."""
import argparse
from azureml.core import Run
import fsspec
import re
import yaml

from azureml.rag.utils.logging import get_logger, enable_stdout_logging
from azureml.rag._asset_client.client import get_rest_client, register_new_data_asset_version

logger = get_logger('register_mlindex')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage-uri", type=str, required=True, dest='storage_uri')
    parser.add_argument("--asset-name", type=str, required=False, dest='asset_name', default='MLIndexAsset')
    parser.add_argument("--output-asset-id", type=str, dest='output_asset_id')
    args = parser.parse_args()

    print('\n'.join(f'{k}={v}' for k, v in vars(args).items()))

    enable_stdout_logging()

    run: Run = Run.get_context()
    ws = run.experiment.workspace

    logger.info(f'Checking for MLIndex at: {args.storage_uri.strip("/")}/MLIndex')
    index_kind = None
    mlindex_yaml = None
    try:
        mlindex_file = fsspec.open(f"{args.storage_uri}/MLIndex", 'r')
        # parse yaml to dict
        with mlindex_file as f:
            mlindex_yaml = yaml.safe_load(f)
            index_kind = mlindex_yaml.get('index', {}).get('kind', None)
    except Exception as e:
        logger.error(f"Could not find MLIndex: {e}")
        raise e

    if index_kind is None:
        logger.error(f"Could not find index.kind in MLIndex: {mlindex_yaml}")
        raise ValueError(f"Could not find index.kind in MLIndex: {mlindex_yaml}")

    client = get_rest_client(ws)
    data_version = register_new_data_asset_version(
        client,
        run,
        args.asset_name,
        args.storage_uri,
        properties={
            'azureml.mlIndexAssetKind': index_kind,
            'azureml.mlIndexAsset': 'true',
            'azureml.mlIndexAssetSource': run.properties.get('azureml.mlIndexAssetSource', 'Unknown'),
            'azureml.mlIndexAssetPipelineRunId': run.properties.get('azureml.pipelinerunid', 'Unknown')
        })

    print(data_version.asset_id)

    asset_id = re.sub('azureml://locations/(.*)/workspaces/(.*)/data', f'azureml://subscriptions/{ws._subscription_id}/resourcegroups/{ws._resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{ws._workspace_name}/data', data_version.asset_id)

    print(asset_id)

    with open(args.output_asset_id, 'w') as f:
        f.write(asset_id)

    logger.info(f"Finished Registering MLIndex Asset '{args.asset_name}', version = {data_version.version_id}")
