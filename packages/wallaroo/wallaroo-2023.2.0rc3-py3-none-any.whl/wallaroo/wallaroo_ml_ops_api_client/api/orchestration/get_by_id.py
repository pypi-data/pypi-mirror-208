from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.get_orchestration_by_id_request import \
    GetOrchestrationByIdRequest
from ...models.get_orchestration_by_id_response import \
    GetOrchestrationByIdResponse
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: GetOrchestrationByIdRequest,

) -> Dict[str, Any]:
    url = "{}/v1/api/orchestration/get_by_id".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[GetOrchestrationByIdResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetOrchestrationByIdResponse.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[GetOrchestrationByIdResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: GetOrchestrationByIdRequest,

) -> Response[GetOrchestrationByIdResponse]:
    """ 
    Args:
        json_body (GetOrchestrationByIdRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOrchestrationByIdResponse]
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
    json_body: GetOrchestrationByIdRequest,

) -> Optional[GetOrchestrationByIdResponse]:
    """ 
    Args:
        json_body (GetOrchestrationByIdRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOrchestrationByIdResponse
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: GetOrchestrationByIdRequest,

) -> Response[GetOrchestrationByIdResponse]:
    """ 
    Args:
        json_body (GetOrchestrationByIdRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOrchestrationByIdResponse]
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
    json_body: GetOrchestrationByIdRequest,

) -> Optional[GetOrchestrationByIdResponse]:
    """ 
    Args:
        json_body (GetOrchestrationByIdRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOrchestrationByIdResponse
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
