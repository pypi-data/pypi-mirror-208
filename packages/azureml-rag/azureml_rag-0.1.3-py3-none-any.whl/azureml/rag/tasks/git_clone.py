# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import os

from azureml.rag.utils.git import clone_repo, get_keyvault_authentication
from azureml.rag.utils.logging import get_logger, enable_stdout_logging

logger = get_logger('git_clone')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-repository", type=str, required=True, dest='git_repository')
    parser.add_argument("--branch-name", type=str, required=False, default=None)
    parser.add_argument("--authentication-key-prefix", type=str, required=False, default=None, help="<PREFIX>-USER and <PREFIX>-PASS are the expected names of two Secrets in the Workspace Key Vault which will be used for authenticated when pulling the given git repo.")
    parser.add_argument("--output-data", type=str, required=True, dest='output_data')
    args = parser.parse_args()

    enable_stdout_logging()

    connection_id = os.environ.get('AZUREML_WORKSPACE_CONNECTION_ID_GIT')
    if connection_id is not None and connection_id != '':
        from azureml.rag.utils.connections import get_connection_by_id_v2

        connection = get_connection_by_id_v2(connection_id)
        if args.git_repository != connection['properties']['target']:
            logger.warning(f"Given git repository '{args.git_repository}' does not match the git repository '{connection['properties']['target']}' specified in the Workspace Connection '{connection_id}'. Using the Workspace Connection git repository.")
        args.git_repository = connection['properties']['target']
        authentication = {'username': connection['properties']['metadata']['username'], 'password': connection['properties']['credentials']['pat']}
    elif args.authentication_key_prefix is not None:
        authentication = get_keyvault_authentication(args.authentication_key_prefix)
    else:
        authentication = None


    clone_repo(args.git_repository, args.output_data, args.branch_name, authentication)

    logger.info('Finished cloning.')
