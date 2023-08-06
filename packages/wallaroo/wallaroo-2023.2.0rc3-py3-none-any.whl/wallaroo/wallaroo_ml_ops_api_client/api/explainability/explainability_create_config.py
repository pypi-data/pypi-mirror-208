from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.explainability_create_config_json_body import \
    ExplainabilityCreateConfigJsonBody
from ...models.explainability_create_config_response_200 import \
    ExplainabilityCreateConfigResponse200
from ...models.explainability_create_config_response_400 import \
    ExplainabilityCreateConfigResponse400
from ...models.explainability_create_config_response_401 import \
    ExplainabilityCreateConfigResponse401
from ...models.explainability_create_config_response_500 import \
    ExplainabilityCreateConfigResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ExplainabilityCreateConfigJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/explainability/create_config".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    if response.status_code == HTTPStatus.OK:
        _response_200 = response.json()
        response_200: Optional[ExplainabilityCreateConfigResponse200]
        if _response_200 is None:
            response_200 = None
        else:
            response_200 = ExplainabilityCreateConfigResponse200.from_dict(_response_200)



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ExplainabilityCreateConfigResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ExplainabilityCreateConfigResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ExplainabilityCreateConfigResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ExplainabilityCreateConfigJsonBody,

) -> Response[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    """ Create an explainability config

     Creates an explainability config that can be used to create and compare analysis.

    Args:
        json_body (ExplainabilityCreateConfigJsonBody):  A configuration for reference and adhoc
            explainability requests

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]
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
    json_body: ExplainabilityCreateConfigJsonBody,

) -> Optional[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    """ Create an explainability config

     Creates an explainability config that can be used to create and compare analysis.

    Args:
        json_body (ExplainabilityCreateConfigJsonBody):  A configuration for reference and adhoc
            explainability requests

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: ExplainabilityCreateConfigJsonBody,

) -> Response[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    """ Create an explainability config

     Creates an explainability config that can be used to create and compare analysis.

    Args:
        json_body (ExplainabilityCreateConfigJsonBody):  A configuration for reference and adhoc
            explainability requests

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]
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
    json_body: ExplainabilityCreateConfigJsonBody,

) -> Optional[Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]]:
    """ Create an explainability config

     Creates an explainability config that can be used to create and compare analysis.

    Args:
        json_body (ExplainabilityCreateConfigJsonBody):  A configuration for reference and adhoc
            explainability requests

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ExplainabilityCreateConfigResponse400, ExplainabilityCreateConfigResponse401, ExplainabilityCreateConfigResponse500, Optional[ExplainabilityCreateConfigResponse200]]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
