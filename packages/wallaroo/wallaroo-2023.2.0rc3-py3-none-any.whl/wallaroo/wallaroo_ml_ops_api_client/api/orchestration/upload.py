from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.upload_payload_doc import UploadPayloadDoc
from ...models.upload_response import UploadResponse
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    multipart_data: UploadPayloadDoc,

) -> Dict[str, Any]:
    url = "{}/v1/api/orchestration/upload".format(
        client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    

    

    

    

    multipart_multipart_data = multipart_data.to_multipart()




    return {
	    "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "files": multipart_multipart_data,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[UploadResponse]:
    if response.status_code == HTTPStatus.ACCEPTED:
        response_202 = UploadResponse.from_dict(response.json())



        return response_202
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[UploadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    multipart_data: UploadPayloadDoc,

) -> Response[UploadResponse]:
    """ 
    Args:
        multipart_data (UploadPayloadDoc):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
     """


    kwargs = _get_kwargs(
        client=client,
multipart_data=multipart_data,

    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Client,
    multipart_data: UploadPayloadDoc,

) -> Optional[UploadResponse]:
    """ 
    Args:
        multipart_data (UploadPayloadDoc):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
     """


    return sync_detailed(
        client=client,
multipart_data=multipart_data,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: UploadPayloadDoc,

) -> Response[UploadResponse]:
    """ 
    Args:
        multipart_data (UploadPayloadDoc):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UploadResponse]
     """


    kwargs = _get_kwargs(
        client=client,
multipart_data=multipart_data,

    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(
            **kwargs
        )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Client,
    multipart_data: UploadPayloadDoc,

) -> Optional[UploadResponse]:
    """ 
    Args:
        multipart_data (UploadPayloadDoc):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UploadResponse
     """


    return (await asyncio_detailed(
        client=client,
multipart_data=multipart_data,

    )).parsed
