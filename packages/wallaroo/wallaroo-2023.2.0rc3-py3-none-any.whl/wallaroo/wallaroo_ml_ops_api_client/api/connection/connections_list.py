from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.connections_list_json_body import ConnectionsListJsonBody
from ...models.connections_list_response_200 import ConnectionsListResponse200
from ...models.connections_list_response_400 import ConnectionsListResponse400
from ...models.connections_list_response_401 import ConnectionsListResponse401
from ...models.connections_list_response_500 import ConnectionsListResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ConnectionsListJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/connections/list".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ConnectionsListResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ConnectionsListResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ConnectionsListResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ConnectionsListResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ConnectionsListJsonBody,

) -> Response[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    """ List all connections

     List Connections

    Args:
        json_body (ConnectionsListJsonBody):  Request to list Connections

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]
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
    json_body: ConnectionsListJsonBody,

) -> Optional[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    """ List all connections

     List Connections

    Args:
        json_body (ConnectionsListJsonBody):  Request to list Connections

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ConnectionsListJsonBody,

) -> Response[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    """ List all connections

     List Connections

    Args:
        json_body (ConnectionsListJsonBody):  Request to list Connections

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]
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
    json_body: ConnectionsListJsonBody,

) -> Optional[Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]]:
    """ List all connections

     List Connections

    Args:
        json_body (ConnectionsListJsonBody):  Request to list Connections

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionsListResponse200, ConnectionsListResponse400, ConnectionsListResponse401, ConnectionsListResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
