from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.status_get_deployment_json_body import \
    StatusGetDeploymentJsonBody
from ...models.status_get_deployment_response_200 import \
    StatusGetDeploymentResponse200
from ...models.status_get_deployment_response_400 import \
    StatusGetDeploymentResponse400
from ...models.status_get_deployment_response_401 import \
    StatusGetDeploymentResponse401
from ...models.status_get_deployment_response_500 import \
    StatusGetDeploymentResponse500
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: StatusGetDeploymentJsonBody,

) -> Dict[str, Any]:
    url = "{}/v1/api/status/get_deployment".format(
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = StatusGetDeploymentResponse200.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = StatusGetDeploymentResponse400.from_dict(response.json())



        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = StatusGetDeploymentResponse401.from_dict(response.json())



        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = StatusGetDeploymentResponse500.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: StatusGetDeploymentJsonBody,

) -> Response[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    """ Deployment statuses are made up of the engine pods and the statuses of the pipelines and models in
    each of the running engines

     Gets the full status of a deployment.

    Args:
        json_body (StatusGetDeploymentJsonBody):  Request for deployment status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]
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
    json_body: StatusGetDeploymentJsonBody,

) -> Optional[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    """ Deployment statuses are made up of the engine pods and the statuses of the pipelines and models in
    each of the running engines

     Gets the full status of a deployment.

    Args:
        json_body (StatusGetDeploymentJsonBody):  Request for deployment status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]
     """


    return sync_detailed(
        client=client,
json_body=json_body,

    ).parsed

async def asyncio_detailed(
    *,
    client: Client,
    json_body: StatusGetDeploymentJsonBody,

) -> Response[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    """ Deployment statuses are made up of the engine pods and the statuses of the pipelines and models in
    each of the running engines

     Gets the full status of a deployment.

    Args:
        json_body (StatusGetDeploymentJsonBody):  Request for deployment status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]
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
    json_body: StatusGetDeploymentJsonBody,

) -> Optional[Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]]:
    """ Deployment statuses are made up of the engine pods and the statuses of the pipelines and models in
    each of the running engines

     Gets the full status of a deployment.

    Args:
        json_body (StatusGetDeploymentJsonBody):  Request for deployment status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[StatusGetDeploymentResponse200, StatusGetDeploymentResponse400, StatusGetDeploymentResponse401, StatusGetDeploymentResponse500]
     """


    return (await asyncio_detailed(
        client=client,
json_body=json_body,

    )).parsed
