import json
from http import HTTPStatus
from typing import Dict, List

import requests

from openapi_client.models import ResponsePipeline
from vessl import vessl_api
from vessl.organization import _get_organization_name
from vessl.util.constant import GET_ARGUMENT_VALUE_URL, GET_CONTEXT_VARIABLE_URL, UPDATE_CONTEXT_VARIABLE_URL
from vessl.util.exception import BadRequestError, NotFoundError, VesslException


class StepContextVariable(object):
    def __init__(self, step: str, key: str, value: str):
        self.step_name = step
        self.key = key
        self.value = value

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


def read_pipeline(pipeline_name: str, **kwargs) -> ResponsePipeline:
    return vessl_api.pipeline_read_api(
        organization_name=_get_organization_name(**kwargs),
        pipeline_name=pipeline_name,
    ).results


def update_context_variables(data: Dict[str, str], **kwargs):
    # TODO: Works only in pipeline step execution contexts.
    # TODO: Find current running pipelines.
    header = {"Context-Type": "application/json"}
    resp = requests.post(
        UPDATE_CONTEXT_VARIABLE_URL, headers=header, data=json.dumps(data),
    )
    if resp.status_code != HTTPStatus.CREATED and resp.status_code != HTTPStatus.OK:
        if resp.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequestError(f"Update context variables failed. \n data: {data}")
        else:
            raise VesslException()


def get_argument_value(key: str, **kwargs) -> StepContextVariable:
    # TODO: works only in pipeline step execution contexts.
    resp = requests.get(GET_ARGUMENT_VALUE_URL + f"/{key}")

    if resp.status_code != HTTPStatus.OK:
        if resp.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequestError(
                f"Get argument value failed. \n key: {key}"
            )
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(
                f"Argument not found. \n key: {key}"
            )
        else:
            raise VesslException()

    parsed_json = json.loads(resp.content)
    # @XXX(seokju) skip json parse temporarily
    return parsed_json["value"]
    # argument_value = StepContextVariable(**parsed_json)
    # return argument_value


def get_context_variable(
    step_name: str, key: str, **kwargs
) -> StepContextVariable:
    # TODO: works only in pipeline step execution contexts.
    resp = requests.get(GET_CONTEXT_VARIABLE_URL + f"/{step_name}/{key}")

    if resp.status_code != HTTPStatus.OK:
        if resp.status_code == HTTPStatus.BAD_REQUEST:
            raise BadRequestError(
                f"Get context variable failed. \n step_name: {step_name}, key: {key}"
            )
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundError(
                f"Context variable not found. \n step_name: {step_name}, key: {key}"
            )
        else:
            raise VesslException()

    parsed_json = json.loads(resp.content)
    # @XXX(seokju) skip json parse temporarily
    return parsed_json["value"]
    # context_variable = StepContextVariable(**parsed_json)
    # return context_variable


def get_context_variables(
    pipeline_name: str, step_name: str, **kwargs
) -> List[StepContextVariable]:
    raise NotImplementedError
