from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.run_log_out_with_run import RunLogOutWithRun
from ...types import Response


def _get_kwargs(
    run_id: int,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/api/v0/runs/{run_id}".format(client.base_url, run_id=run_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[RunLogOutWithRun]:
    if response.status_code == HTTPStatus.OK:
        response_200 = RunLogOutWithRun.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[RunLogOutWithRun]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    run_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[RunLogOutWithRun]:
    """Get Run

     Gets a DAG run by ID

    @param request:
    @param run_id: The DAG run ID to query
    @return: The DAG run we get from the DB

    Args:
        run_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RunLogOutWithRun]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    run_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[RunLogOutWithRun]:
    """Get Run

     Gets a DAG run by ID

    @param request:
    @param run_id: The DAG run ID to query
    @return: The DAG run we get from the DB

    Args:
        run_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RunLogOutWithRun
    """

    return sync_detailed(
        run_id=run_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    run_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[RunLogOutWithRun]:
    """Get Run

     Gets a DAG run by ID

    @param request:
    @param run_id: The DAG run ID to query
    @return: The DAG run we get from the DB

    Args:
        run_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RunLogOutWithRun]
    """

    kwargs = _get_kwargs(
        run_id=run_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    run_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[RunLogOutWithRun]:
    """Get Run

     Gets a DAG run by ID

    @param request:
    @param run_id: The DAG run ID to query
    @return: The DAG run we get from the DB

    Args:
        run_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RunLogOutWithRun
    """

    return (
        await asyncio_detailed(
            run_id=run_id,
            client=client,
        )
    ).parsed
