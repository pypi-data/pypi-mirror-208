from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.users_activate_json_body import UsersActivateJsonBody
from ...models.users_activate_response_200 import UsersActivateResponse200
from ...models.users_activate_response_400 import UsersActivateResponse400
from ...models.users_activate_response_401 import UsersActivateResponse401
from ...models.users_activate_response_500 import UsersActivateResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: UsersActivateJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/users/activate".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = UsersActivateResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = UsersActivateResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = UsersActivateResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = UsersActivateResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: UsersActivateJsonBody,

) -> Response[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    """ Activate user

     Activate a previously deactivated user.

    Args:
        json_body (UsersActivateJsonBody):  Request to update an existing user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]
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
    json_body: UsersActivateJsonBody,

) -> Optional[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    """ Activate user

     Activate a previously deactivated user.

    Args:
        json_body (UsersActivateJsonBody):  Request to update an existing user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: UsersActivateJsonBody,

) -> Response[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    """ Activate user

     Activate a previously deactivated user.

    Args:
        json_body (UsersActivateJsonBody):  Request to update an existing user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]
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
    json_body: UsersActivateJsonBody,

) -> Optional[Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]]:
    """ Activate user

     Activate a previously deactivated user.

    Args:
        json_body (UsersActivateJsonBody):  Request to update an existing user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[UsersActivateResponse200, UsersActivateResponse400, UsersActivateResponse401, UsersActivateResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
