from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.invocation_result import InvocationResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    vin: str,
    *,
    client: Client,
    vcc_api_operation_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/vehicles/{vin}/commands/lock".format(client.base_url, vin=vin)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(vcc_api_operation_id, Unset):
        headers["vcc-api-operationId"] = vcc_api_operation_id

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[ErrorResponse, InvocationResult]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = InvocationResult.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
        response_415 = ErrorResponse.from_dict(response.json())

        return response_415
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503
    if response.status_code == HTTPStatus.GATEWAY_TIMEOUT:
        response_504 = ErrorResponse.from_dict(response.json())

        return response_504
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ErrorResponse, InvocationResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    vin: str,
    *,
    client: Client,
    vcc_api_operation_id: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, InvocationResult]]:
    """Lock doors

     Used to send a lock command to the vehicle.

    Args:
        vin (str):
        vcc_api_operation_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, InvocationResult]]
    """

    kwargs = _get_kwargs(
        vin=vin,
        client=client,
        vcc_api_operation_id=vcc_api_operation_id,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    vin: str,
    *,
    client: Client,
    vcc_api_operation_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, InvocationResult]]:
    """Lock doors

     Used to send a lock command to the vehicle.

    Args:
        vin (str):
        vcc_api_operation_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, InvocationResult]
    """

    return sync_detailed(
        vin=vin,
        client=client,
        vcc_api_operation_id=vcc_api_operation_id,
    ).parsed


async def asyncio_detailed(
    vin: str,
    *,
    client: Client,
    vcc_api_operation_id: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, InvocationResult]]:
    """Lock doors

     Used to send a lock command to the vehicle.

    Args:
        vin (str):
        vcc_api_operation_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, InvocationResult]]
    """

    kwargs = _get_kwargs(
        vin=vin,
        client=client,
        vcc_api_operation_id=vcc_api_operation_id,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    vin: str,
    *,
    client: Client,
    vcc_api_operation_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, InvocationResult]]:
    """Lock doors

     Used to send a lock command to the vehicle.

    Args:
        vin (str):
        vcc_api_operation_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, InvocationResult]
    """

    return (
        await asyncio_detailed(
            vin=vin,
            client=client,
            vcc_api_operation_id=vcc_api_operation_id,
        )
    ).parsed
