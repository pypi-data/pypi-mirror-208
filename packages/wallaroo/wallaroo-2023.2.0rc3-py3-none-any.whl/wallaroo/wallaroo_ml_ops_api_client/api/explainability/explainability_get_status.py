from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.explainability_get_status_response_200 import \
    ExplainabilityGetStatusResponse200
from ...models.explainability_get_status_response_400 import \
    ExplainabilityGetStatusResponse400
from ...models.explainability_get_status_response_401 import \
    ExplainabilityGetStatusResponse401
from ...models.explainability_get_status_response_500 import \
    ExplainabilityGetStatusResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,

) -> Dict[str, Any]:
    url = "{}/v1/api/explainability/get_status".format(
        client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    

    

    

    return {
	    "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ExplainabilityGetStatusResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ExplainabilityGetStatusResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ExplainabilityGetStatusResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ExplainabilityGetStatusResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,

) -> Response[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    """ Get explainability status

     Get the status of the explainability feature.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]
     """


    kwargs = _get_kwargs(
        client=client,

    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Client,

) -> Optional[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    """ Get explainability status

     Get the status of the explainability feature.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]
     """


    return sync_detailed(
        client=client,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,

) -> Response[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    """ Get explainability status

     Get the status of the explainability feature.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]
     """


    kwargs = _get_kwargs(
        client=client,

    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(
            **kwargs
        )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Client,

) -> Optional[Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]]:
    """ Get explainability status

     Get the status of the explainability feature.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityGetStatusResponse200, ExplainabilityGetStatusResponse400, ExplainabilityGetStatusResponse401, ExplainabilityGetStatusResponse500]
     """


    return (await asyncio_detailed(
        client=client,

    )).parsed
