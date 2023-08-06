from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.connections_remove_from_workspace_json_body import \
    ConnectionsRemoveFromWorkspaceJsonBody
from ...models.connections_remove_from_workspace_response_400 import \
    ConnectionsRemoveFromWorkspaceResponse400
from ...models.connections_remove_from_workspace_response_401 import \
    ConnectionsRemoveFromWorkspaceResponse401
from ...models.connections_remove_from_workspace_response_500 import \
    ConnectionsRemoveFromWorkspaceResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ConnectionsRemoveFromWorkspaceJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/connections/remove_from_workspace".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ConnectionsRemoveFromWorkspaceResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ConnectionsRemoveFromWorkspaceResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ConnectionsRemoveFromWorkspaceResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ConnectionsRemoveFromWorkspaceJsonBody,

) -> Response[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    """ Remove a connection from a workspace

     Remove a connection from a workspace

    Args:
        json_body (ConnectionsRemoveFromWorkspaceJsonBody):  Request to remove a Connection from
            Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]
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
    json_body: ConnectionsRemoveFromWorkspaceJsonBody,

) -> Optional[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    """ Remove a connection from a workspace

     Remove a connection from a workspace

    Args:
        json_body (ConnectionsRemoveFromWorkspaceJsonBody):  Request to remove a Connection from
            Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ConnectionsRemoveFromWorkspaceJsonBody,

) -> Response[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    """ Remove a connection from a workspace

     Remove a connection from a workspace

    Args:
        json_body (ConnectionsRemoveFromWorkspaceJsonBody):  Request to remove a Connection from
            Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]
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
    json_body: ConnectionsRemoveFromWorkspaceJsonBody,

) -> Optional[Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]]:
    """ Remove a connection from a workspace

     Remove a connection from a workspace

    Args:
        json_body (ConnectionsRemoveFromWorkspaceJsonBody):  Request to remove a Connection from
            Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ConnectionsRemoveFromWorkspaceResponse400, ConnectionsRemoveFromWorkspaceResponse401, ConnectionsRemoveFromWorkspaceResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
