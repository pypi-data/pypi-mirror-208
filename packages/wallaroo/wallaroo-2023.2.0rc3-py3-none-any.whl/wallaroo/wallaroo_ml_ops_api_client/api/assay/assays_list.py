from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.assays_list_json_body import AssaysListJsonBody
from ...models.assays_list_response_200_item import AssaysListResponse200Item
from ...models.assays_list_response_400 import AssaysListResponse400
from ...models.assays_list_response_401 import AssaysListResponse401
from ...models.assays_list_response_500 import AssaysListResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: AssaysListJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/assays/list".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = AssaysListResponse200Item.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = AssaysListResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = AssaysListResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = AssaysListResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: AssaysListJsonBody,

) -> Response[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    """ List assays

     Returns the list of existing assays.

    Args:
        json_body (AssaysListJsonBody):  Request for list of assays.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]
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
    json_body: AssaysListJsonBody,

) -> Optional[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    """ List assays

     Returns the list of existing assays.

    Args:
        json_body (AssaysListJsonBody):  Request for list of assays.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: AssaysListJsonBody,

) -> Response[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    """ List assays

     Returns the list of existing assays.

    Args:
        json_body (AssaysListJsonBody):  Request for list of assays.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]
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
    json_body: AssaysListJsonBody,

) -> Optional[Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]]:
    """ List assays

     Returns the list of existing assays.

    Args:
        json_body (AssaysListJsonBody):  Request for list of assays.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AssaysListResponse400, AssaysListResponse401, AssaysListResponse500, List['AssaysListResponse200Item']]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
