from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.plateau_get_topic_name_json_body import \
    PlateauGetTopicNameJsonBody
from ...models.plateau_get_topic_name_response_200 import \
    PlateauGetTopicNameResponse200
from ...models.plateau_get_topic_name_response_400 import \
    PlateauGetTopicNameResponse400
from ...models.plateau_get_topic_name_response_401 import \
    PlateauGetTopicNameResponse401
from ...models.plateau_get_topic_name_response_500 import \
    PlateauGetTopicNameResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: PlateauGetTopicNameJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/plateau/get_topic_name".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PlateauGetTopicNameResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PlateauGetTopicNameResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = PlateauGetTopicNameResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = PlateauGetTopicNameResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: PlateauGetTopicNameJsonBody,

) -> Response[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    """ Get topic name

     Returns the topic name for the given pipeline.

    Args:
        json_body (PlateauGetTopicNameJsonBody):  Request for topic name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]
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
    json_body: PlateauGetTopicNameJsonBody,

) -> Optional[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    """ Get topic name

     Returns the topic name for the given pipeline.

    Args:
        json_body (PlateauGetTopicNameJsonBody):  Request for topic name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: PlateauGetTopicNameJsonBody,

) -> Response[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    """ Get topic name

     Returns the topic name for the given pipeline.

    Args:
        json_body (PlateauGetTopicNameJsonBody):  Request for topic name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]
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
    json_body: PlateauGetTopicNameJsonBody,

) -> Optional[Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]]:
    """ Get topic name

     Returns the topic name for the given pipeline.

    Args:
        json_body (PlateauGetTopicNameJsonBody):  Request for topic name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PlateauGetTopicNameResponse200, PlateauGetTopicNameResponse400, PlateauGetTopicNameResponse401, PlateauGetTopicNameResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
