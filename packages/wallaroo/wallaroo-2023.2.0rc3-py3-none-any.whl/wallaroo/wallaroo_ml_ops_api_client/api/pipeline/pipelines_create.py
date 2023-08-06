from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.pipelines_create_json_body import PipelinesCreateJsonBody
from ...models.pipelines_create_response_200 import PipelinesCreateResponse200
from ...models.pipelines_create_response_400 import PipelinesCreateResponse400
from ...models.pipelines_create_response_401 import PipelinesCreateResponse401
from ...models.pipelines_create_response_500 import PipelinesCreateResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: PipelinesCreateJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/pipelines/create".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PipelinesCreateResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PipelinesCreateResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = PipelinesCreateResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = PipelinesCreateResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: PipelinesCreateJsonBody,

) -> Response[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    """ Create a new pipeline

     Creates a new pipeline.

    Args:
        json_body (PipelinesCreateJsonBody):  Request to create a new pipeline in a workspace.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]
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
    json_body: PipelinesCreateJsonBody,

) -> Optional[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    """ Create a new pipeline

     Creates a new pipeline.

    Args:
        json_body (PipelinesCreateJsonBody):  Request to create a new pipeline in a workspace.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: PipelinesCreateJsonBody,

) -> Response[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    """ Create a new pipeline

     Creates a new pipeline.

    Args:
        json_body (PipelinesCreateJsonBody):  Request to create a new pipeline in a workspace.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]
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
    json_body: PipelinesCreateJsonBody,

) -> Optional[Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]]:
    """ Create a new pipeline

     Creates a new pipeline.

    Args:
        json_body (PipelinesCreateJsonBody):  Request to create a new pipeline in a workspace.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PipelinesCreateResponse200, PipelinesCreateResponse400, PipelinesCreateResponse401, PipelinesCreateResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
