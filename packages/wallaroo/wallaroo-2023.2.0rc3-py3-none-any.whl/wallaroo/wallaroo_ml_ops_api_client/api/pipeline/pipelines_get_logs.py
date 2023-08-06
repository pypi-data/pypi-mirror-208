from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.pipelines_get_logs_json_body import PipelinesGetLogsJsonBody
from ...models.pipelines_get_logs_response_400 import \
    PipelinesGetLogsResponse400
from ...models.pipelines_get_logs_response_401 import \
    PipelinesGetLogsResponse401
from ...models.pipelines_get_logs_response_500 import \
    PipelinesGetLogsResponse500
from ...models.pipelines_get_logs_response_502 import \
    PipelinesGetLogsResponse502
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: PipelinesGetLogsJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/pipelines/get_logs".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PipelinesGetLogsResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = PipelinesGetLogsResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = PipelinesGetLogsResponse500.from_dict(response.json())



        return response_500
    if response.status_code == HTTPStatus.BAD_GATEWAY:
        response_502 = PipelinesGetLogsResponse502.from_dict(response.json())



        return response_502
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: PipelinesGetLogsJsonBody,

) -> Response[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    """ Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        json_body (PipelinesGetLogsJsonBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]
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
    json_body: PipelinesGetLogsJsonBody,

) -> Optional[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    """ Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        json_body (PipelinesGetLogsJsonBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: PipelinesGetLogsJsonBody,

) -> Response[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    """ Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        json_body (PipelinesGetLogsJsonBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]
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
    json_body: PipelinesGetLogsJsonBody,

) -> Optional[Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]:
    """ Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        json_body (PipelinesGetLogsJsonBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
