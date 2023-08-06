# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language model classes."""
import json
from langchain.llms import AzureOpenAI
try:
    # Some after 0.0.149 this was moved.
    from langchain.schema import BaseLanguageModel
except ImportError:
    from langchain.base_language import BaseLanguageModel
from langchain.chat_models.azure_openai import AzureChatOpenAI

from azureml.rag.utils.logging import get_logger


logger = get_logger(__name__)


def parse_model_uri(uri: str, **kwargs) -> dict:
    """Parse a model URI into a dictionary of configuration parameters."""
    scheme, details = uri.split('://')

    def split_details(details):
        details = details.split('/')
        dets = {}
        for i in range(0, len(details), 2):
            dets[details[i]] = details[i + 1]
        return dets

    config = {**kwargs}
    if scheme == 'azure_open_ai':
        config = {**split_details(details), **config}
        config['kind'] = 'open_ai'
        if 'endpoint' in config:
            config['api_base'] = f"https://{config['endpoint']}.openai.azure.com"
        elif 'endpoint' in kwargs:
            config['api_base'] = f"https://{kwargs['endpoint']}.openai.azure.com"
        config['api_type'] = 'azure'
        config['api_version'] = kwargs.get('api_version') if kwargs.get('api_version') is not None else '2023-03-15-preview'
        # Azure OpenAI has a batch_size limit of 1
        config['batch_size'] = '1'
    elif scheme == 'open_ai':
        config['kind'] = 'open_ai'
        config = {**split_details(details), **config}
        config['api_type'] = 'open_ai'
    elif scheme == 'hugging_face':
        config['kind'] = 'hugging_face'
        config['model'] = details.split('model/')[1]
    elif scheme == 'none':
        config['kind'] = 'none'
    else:
        raise ValueError(f'Unknown model kind: {scheme}')

    return config


def init_llm(model_config: dict) -> BaseLanguageModel:
    """Initialize a language model from a model configuration."""
    llm = None
    logger.debug(f"model_config: {json.dumps(model_config, indent=2)}")
    if model_config.get('kind') == 'open_ai' and model_config.get('api_type') == 'azure':
        if model_config['model'].startswith("gpt-3.5-turbo") or model_config['model'].startswith("gpt-35-turbo") or model_config['model'].startswith("gpt-4"):
            logger.info(f"Initializing AzureChatOpenAI with model {model_config['model']}")
            model_kwargs = {
                "engine": model_config['deployment'],
                "frequency_penalty": model_config.get('frequency_penalty', 0),
                "presence_penalty": model_config.get('presence_penalty', 0),
                "stop": model_config.get('stop'),
            }
            llm = AzureChatOpenAI(
                deployment_name=model_config['deployment'],
                model_name=model_config['model'],
                temperature=model_config.get('temperature'),
                max_tokens=model_config.get('max_tokens'),
                model_kwargs=model_kwargs,
                openai_api_key=model_config.get('key'),
                openai_api_base=model_config.get('api_base'),
                openai_api_type=model_config.get('api_type'),
                openai_api_version=model_config.get('api_version')
            )  # type: ignore
        else:
            print(f"Initializing AzureOpenAI with model {model_config['model']}")
            llm = AzureOpenAI(
                deployment_name=model_config['deployment'],
                model_name=model_config['model'],
                temperature=model_config.get('temperature'),
                max_tokens=model_config.get('max_tokens'),
                model_kwargs={"stop": model_config.get('stop')},
                openai_api_key=model_config.get('key')
            )  # type: ignore
    else:
        raise ValueError(f"Unsupported llm kind: {model_config.get('kind')}")

    return llm
