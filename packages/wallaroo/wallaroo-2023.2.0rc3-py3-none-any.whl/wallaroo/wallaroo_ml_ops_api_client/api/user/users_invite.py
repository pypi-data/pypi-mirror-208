from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.users_invite_json_body import UsersInviteJsonBody
from ...models.users_invite_response_200 import UsersInviteResponse200
from ...models.users_invite_response_400 import UsersInviteResponse400
from ...models.users_invite_response_401 import UsersInviteResponse401
from ...models.users_invite_response_500 import UsersInviteResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: UsersInviteJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/users/invite".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = UsersInviteResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = UsersInviteResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = UsersInviteResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = UsersInviteResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: UsersInviteJsonBody,

) -> Response[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    """ Invite user to Wallaroo

     Invite a new user to your Wallaroo cluster by sending them an invitation email.

    Args:
        json_body (UsersInviteJsonBody):  Invitation request for a new user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]
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
    json_body: UsersInviteJsonBody,

) -> Optional[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    """ Invite user to Wallaroo

     Invite a new user to your Wallaroo cluster by sending them an invitation email.

    Args:
        json_body (UsersInviteJsonBody):  Invitation request for a new user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: UsersInviteJsonBody,

) -> Response[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    """ Invite user to Wallaroo

     Invite a new user to your Wallaroo cluster by sending them an invitation email.

    Args:
        json_body (UsersInviteJsonBody):  Invitation request for a new user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]
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
    json_body: UsersInviteJsonBody,

) -> Optional[Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]]:
    """ Invite user to Wallaroo

     Invite a new user to your Wallaroo cluster by sending them an invitation email.

    Args:
        json_body (UsersInviteJsonBody):  Invitation request for a new user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UsersInviteResponse200, UsersInviteResponse400, UsersInviteResponse401, UsersInviteResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
