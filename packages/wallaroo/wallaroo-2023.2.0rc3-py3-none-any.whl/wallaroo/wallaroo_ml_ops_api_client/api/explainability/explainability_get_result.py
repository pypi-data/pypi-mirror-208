from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.explainability_get_result_json_body import \
    ExplainabilityGetResultJsonBody
from ...models.explainability_get_result_response_200 import \
    ExplainabilityGetResultResponse200
from ...models.explainability_get_result_response_400 import \
    ExplainabilityGetResultResponse400
from ...models.explainability_get_result_response_401 import \
    ExplainabilityGetResultResponse401
from ...models.explainability_get_result_response_500 import \
    ExplainabilityGetResultResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ExplainabilityGetResultJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/explainability/get_result".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    if response.status_code == HTTPStatus.OK:
        _response_200 = response.json()
        response_200: Optional[ExplainabilityGetResultResponse200]
        if _response_200 is None:
            response_200 = None
        else:
            response_200 = ExplainabilityGetResultResponse200.from_dict(_response_200)



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ExplainabilityGetResultResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ExplainabilityGetResultResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ExplainabilityGetResultResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ExplainabilityGetResultJsonBody,

) -> Response[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    """ Get explainability result

     Gets the result of an explainability request.

    Args:
        json_body (ExplainabilityGetResultJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]
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
    json_body: ExplainabilityGetResultJsonBody,

) -> Optional[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    """ Get explainability result

     Gets the result of an explainability request.

    Args:
        json_body (ExplainabilityGetResultJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ExplainabilityGetResultJsonBody,

) -> Response[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    """ Get explainability result

     Gets the result of an explainability request.

    Args:
        json_body (ExplainabilityGetResultJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]
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
    json_body: ExplainabilityGetResultJsonBody,

) -> Optional[Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]]:
    """ Get explainability result

     Gets the result of an explainability request.

    Args:
        json_body (ExplainabilityGetResultJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityGetResultResponse400, ExplainabilityGetResultResponse401, ExplainabilityGetResultResponse500, Optional[ExplainabilityGetResultResponse200]]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
