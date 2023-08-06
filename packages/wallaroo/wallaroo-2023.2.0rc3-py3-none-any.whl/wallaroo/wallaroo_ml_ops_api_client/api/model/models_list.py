from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.models_list_json_body import ModelsListJsonBody
from ...models.models_list_response_200 import ModelsListResponse200
from ...models.models_list_response_400 import ModelsListResponse400
from ...models.models_list_response_401 import ModelsListResponse401
from ...models.models_list_response_500 import ModelsListResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ModelsListJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/models/list".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ModelsListResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ModelsListResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ModelsListResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ModelsListResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ModelsListJsonBody,

) -> Response[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    """ Retrieve models

     Returns models in the given workspace.

    Args:
        json_body (ModelsListJsonBody):  Workspace model retrieval request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]
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
    json_body: ModelsListJsonBody,

) -> Optional[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    """ Retrieve models

     Returns models in the given workspace.

    Args:
        json_body (ModelsListJsonBody):  Workspace model retrieval request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ModelsListJsonBody,

) -> Response[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    """ Retrieve models

     Returns models in the given workspace.

    Args:
        json_body (ModelsListJsonBody):  Workspace model retrieval request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]
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
    json_body: ModelsListJsonBody,

) -> Optional[Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]]:
    """ Retrieve models

     Returns models in the given workspace.

    Args:
        json_body (ModelsListJsonBody):  Workspace model retrieval request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ModelsListResponse200, ModelsListResponse400, ModelsListResponse401, ModelsListResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
