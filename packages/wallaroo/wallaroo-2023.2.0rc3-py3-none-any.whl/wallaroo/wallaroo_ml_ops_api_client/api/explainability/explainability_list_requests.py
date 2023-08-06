from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.explainability_list_requests_json_body import \
    ExplainabilityListRequestsJsonBody
from ...models.explainability_list_requests_response_200_item import \
    ExplainabilityListRequestsResponse200Item
from ...models.explainability_list_requests_response_400 import \
    ExplainabilityListRequestsResponse400
from ...models.explainability_list_requests_response_401 import \
    ExplainabilityListRequestsResponse401
from ...models.explainability_list_requests_response_500 import \
    ExplainabilityListRequestsResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ExplainabilityListRequestsJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/explainability/list_requests".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            _response_200_item = response_200_item_data
            response_200_item: Optional[ExplainabilityListRequestsResponse200Item]
            if _response_200_item is None:
                response_200_item = None
            else:
                response_200_item = ExplainabilityListRequestsResponse200Item.from_dict(_response_200_item)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ExplainabilityListRequestsResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ExplainabilityListRequestsResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ExplainabilityListRequestsResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ExplainabilityListRequestsJsonBody,

) -> Response[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    """ List explainability requests

     Gets the explainability requests for a particular config.

    Args:
        json_body (ExplainabilityListRequestsJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]
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
    json_body: ExplainabilityListRequestsJsonBody,

) -> Optional[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    """ List explainability requests

     Gets the explainability requests for a particular config.

    Args:
        json_body (ExplainabilityListRequestsJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ExplainabilityListRequestsJsonBody,

) -> Response[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    """ List explainability requests

     Gets the explainability requests for a particular config.

    Args:
        json_body (ExplainabilityListRequestsJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]
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
    json_body: ExplainabilityListRequestsJsonBody,

) -> Optional[Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]]:
    """ List explainability requests

     Gets the explainability requests for a particular config.

    Args:
        json_body (ExplainabilityListRequestsJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityListRequestsResponse400, ExplainabilityListRequestsResponse401, ExplainabilityListRequestsResponse500, List[Optional['ExplainabilityListRequestsResponse200Item']]]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
