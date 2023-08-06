# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex auth connection utilities."""
import requests
import tenacity
import json
import re

from azureml.rag.utils.logging import get_logger


logger = get_logger('connections')


def get_connection_credential(config):
    """Get a credential for a connection."""
    try:
        from azure.core.credentials import AzureKeyCredential  # noqa:F401
    except ImportError as e:
        raise ValueError(
            "Could not import azure-core python package. "
            "Please install it with `pip install azure-core`."
        ) from e
    try:
        from azure.identity import DefaultAzureCredential  # noqa:F401
    except ImportError as e:
        raise ValueError(
            "Could not import azure-identity python package. "
            "Please install it with `pip install azure-identity`."
        ) from e
    if config.get('connection_type', None) == 'workspace_keyvault':
        from azureml.core import Run, Workspace
        run = Run.get_context()
        if hasattr(run, 'experiment'):
            ws = run.experiment.workspace
        else:
            try:
                ws = Workspace(
                    subscription_id=config.get('connection', {}).get('subscription'),
                    resource_group=config.get('connection', {}).get('resource_group'),
                    workspace_name=config.get('connection', {}).get('workspace')
                )
            except Exception as e:
                logger.warning(f"Could not get workspace '{config.get('connection', {}).get('workspace')}': {e}")
                # Fall back to looking for key in environment.
                import os
                key = os.environ.get(config.get('connection', {}).get('key'))
                if key is None:
                    raise ValueError(f"Could not get workspace '{config.get('connection', {}).get('workspace')}' and no key named '{config.get('connection', {}).get('key')}' in environment")
                return AzureKeyCredential(key)

        keyvault = ws.get_default_keyvault()
        credential = AzureKeyCredential(keyvault.get_secret(config.get('connection', {}).get('key')))
    elif config.get('connection_type', None) == 'workspace_connection':
        connection_id = config.get('connection', {}).get('id')
        connection = get_connection_by_id_v2(connection_id)
        credential = workspace_connection_to_credential(connection)
    elif config.get('connection_type', None) == 'environment':
        import os
        key = os.environ.get(config.get('connection', {}).get('key', 'OPENAI-API-KEY'))
        if key is None:
            credential = DefaultAzureCredential()
        else:
            credential = AzureKeyCredential(key)
    else:
        credential = DefaultAzureCredential()
    return credential


def workspace_connection_to_credential(ws_connection):
    """Get a credential for a workspace connection."""
    if ws_connection['properties']['authType'] == 'ApiKey':
        from azure.core.credentials import AzureKeyCredential
        return AzureKeyCredential(ws_connection['properties']['credentials']['key'])
    elif ws_connection['properties']['authType'] == 'PAT':
        from azure.core.credentials import AccessToken
        return AccessToken(ws_connection['properties']['credentials']['pat'], ws_connection['properties'].get('expiresOn', None))
    else:
        raise ValueError(f"Unknown auth type '{ws_connection['properties']['authType']}'")


@tenacity.retry(
    wait=tenacity.wait_fixed(5),  # wait 5 seconds between retries
    stop=tenacity.stop_after_attempt(3),  # stop after 3 attempts
    reraise=True,  # re-raise the exception after the last retry attempt
)
def send_post_request(url, headers, payload):
    """Send a POST request."""""
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    # Raise an exception if the response contains an HTTP error status code
    response.raise_for_status()
    return response


def get_connection_by_name_v2(workspace, name: str) -> dict:
    """Get a connection from a workspace."""
    if hasattr(workspace._auth, 'get_token'):
        bearer_token = workspace._auth.get_token('https://management.azure.com/.default').token
    else:
        bearer_token = workspace._auth.token

    endpoint = workspace.service_context._get_endpoint('api')
    url = f"{endpoint}/rp/workspaces/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}/listsecrets?api-version=2023-02-01-preview"
    resp = send_post_request(url, {
        'Authorization': f'Bearer {bearer_token}',
        'content-type': 'application/json'
    }, {})

    return resp.json()


def get_connection_by_id_v2(connection_id: str) -> dict:
    """Get a connection from a workspace."""
    uri_match = re.match(r'/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)', connection_id)

    logger.info(f'Getting workspace connection: {uri_match.group(4)}')

    from azureml.core import Run, Workspace
    run = Run.get_context()
    if hasattr(run, 'experiment'):
        ws = run.experiment.workspace
    else:
        try:
            ws = Workspace(
                subscription_id=uri_match.group(1),
                resource_group=uri_match.group(2),
                workspace_name=uri_match.group(3)
            )
        except Exception as e:
            logger.warning(f"Could not get workspace '{uri_match.group(3)}': {e}")
            raise ValueError(f"Could not get workspace '{uri_match.group(3)}'") from e

    return get_connection_by_name_v2(ws, uri_match.group(4))


@tenacity.retry(
    wait=tenacity.wait_fixed(5),  # wait 5 seconds between retries
    stop=tenacity.stop_after_attempt(3),  # stop after 3 attempts
    reraise=True,  # re-raise the exception after the last retry attempt
)
def send_put_request(url, headers, payload):
    """Send a PUT request."""""
    response = requests.put(url, data=json.dumps(payload), headers=headers)
    print(response.text)
    # Raise an exception if the response contains an HTTP error status code
    response.raise_for_status()
    return response


def create_connection_v2(workspace, name, category: str, target: str, auth_type: str, credentials: dict, metadata: str):
    """Create a connection in a workspace."""
    url = f"https://management.azure.com/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}?api-version=2023-04-01-preview"

    resp = send_put_request(url, {
        "Authorization": f"Bearer {workspace._auth.get_token('https://management.azure.com/.default').token}",
        "content-type": "application/json"
    }, {
        "properties": {
            "category": category,
            "target": target,
            "authType": auth_type,
            "credentials": credentials,
            "metadata": metadata
        }
    })

    return resp.json()
