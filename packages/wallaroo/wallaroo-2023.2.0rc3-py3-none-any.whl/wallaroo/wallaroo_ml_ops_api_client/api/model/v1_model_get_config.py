from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.v1_model_get_config_json_body import V1ModelGetConfigJsonBody
from ...models.v1_model_get_config_response_200 import \
    V1ModelGetConfigResponse200
from ...models.v1_model_get_config_response_400 import \
    V1ModelGetConfigResponse400
from ...models.v1_model_get_config_response_401 import \
    V1ModelGetConfigResponse401
from ...models.v1_model_get_config_response_500 import \
    V1ModelGetConfigResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: V1ModelGetConfigJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/models/get_config_by_id".format(
        client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    

    json_json_body = json_body.to_dict()



    

    return {
	    "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = V1ModelGetConfigResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = V1ModelGetConfigResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = V1ModelGetConfigResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = V1ModelGetConfigResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: V1ModelGetConfigJsonBody,

) -> Response[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    """ Get latest model config, by a model id.

     Retrieve the latest model configuration, by a model id.

    Args:
        json_body (V1ModelGetConfigJsonBody):  Body for request to /models/get_config_by_id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]
     """


    kwargs = _get_kwargs(
        client=client,
json_body=json_body,

    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Client,
    json_body: V1ModelGetConfigJsonBody,

) -> Optional[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    """ Get latest model config, by a model id.

     Retrieve the latest model configuration, by a model id.

    Args:
        json_body (V1ModelGetConfigJsonBody):  Body for request to /models/get_config_by_id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: V1ModelGetConfigJsonBody,

) -> Response[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    """ Get latest model config, by a model id.

     Retrieve the latest model configuration, by a model id.

    Args:
        json_body (V1ModelGetConfigJsonBody):  Body for request to /models/get_config_by_id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]
     """


    kwargs = _get_kwargs(
        client=client,
json_body=json_body,

    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(
            **kwargs
        )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Client,
    json_body: V1ModelGetConfigJsonBody,

) -> Optional[Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]]:
    """ Get latest model config, by a model id.

     Retrieve the latest model configuration, by a model id.

    Args:
        json_body (V1ModelGetConfigJsonBody):  Body for request to /models/get_config_by_id

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[V1ModelGetConfigResponse200, V1ModelGetConfigResponse400, V1ModelGetConfigResponse401, V1ModelGetConfigResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
