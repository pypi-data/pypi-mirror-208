from asyncio.log import logger

from botocore.config import Config
import botocore.exceptions
from typing import Dict, Optional, List
import boto3
from cachetools import cached, TTLCache
from pydantic import BaseModel

TTL = 12 * 60 * 60 
MAXSIZE = 5000

client = boto3.client('ssm')

def _get_parameter_value(name:str) -> Optional[str]:
    try:
        response = client.get_parameter(Name=name)
        return response["Parameter"]["Value"]
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return None
        else:
            raise e

def _get_parameter_not_cached(name: str, modelType: type[BaseModel]) -> Optional[str]:
    value = _get_parameter_value(name=name)
    if value:
        return modelType.parse_raw(value)
    else:
        return None

@cached(cache=TTLCache(maxsize=MAXSIZE, ttl=TTL))
def _get_parameter_cached(name: str, modelType: type[BaseModel]) -> Optional[str]:
    return _get_parameter_not_cached(name, modelType)


def get_parameter_names() -> List[str]:
    responses = client.get_parameters_by_path(Path="/")
    # TODO: Support Pagination
    return [parameter['Name'] for parameter in responses["Parameters"]]

def get_parameter(name: str, modelType: type[BaseModel], cached=True) -> Optional[str]:
    if cached:
        return _get_parameter_cached(name, modelType)
    else: 
        return _get_parameter_not_cached(name, modelType)
    
def get_parameter_value(name: str) -> Optional[str]:
    return _get_parameter_value(name=name)

def put_parameter(name: str, modelType: type[BaseModel], value_str: str):
    # To validate
    modelType.parse_raw(value_str)

    client.put_parameter(
        Name=name,
        Type='String',
        Overwrite=True,
        Value=value_str
    )
