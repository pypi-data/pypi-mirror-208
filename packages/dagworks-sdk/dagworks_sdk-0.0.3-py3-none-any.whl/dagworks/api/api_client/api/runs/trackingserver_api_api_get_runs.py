from http import HTTPStatus
from typing import Any, Dict, List, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.run_log_out_with_run import RunLogOutWithRun
from ...types import Response


def _get_kwargs(
    run_ids: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/api/v0/runs/bulk/{run_ids}".format(client.base_url, run_ids=run_ids)

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


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[List["RunLogOutWithRun"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RunLogOutWithRun.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[List["RunLogOutWithRun"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    run_ids: str,
    *,
    client: AuthenticatedClient,
) -> Response[List["RunLogOutWithRun"]]:
    """Get Runs

     Bulk queries run IDs. This will return a list of runs, in the same order as the run IDs.

    @param request:
    @param run_ids: The DAG run ID to query -- comma separated
    @return: The DAG run we get from the DB

    Args:
        run_ids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['RunLogOutWithRun']]
    """

    kwargs = _get_kwargs(
        run_ids=run_ids,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    run_ids: str,
    *,
    client: AuthenticatedClient,
) -> Optional[List["RunLogOutWithRun"]]:
    """Get Runs

     Bulk queries run IDs. This will return a list of runs, in the same order as the run IDs.

    @param request:
    @param run_ids: The DAG run ID to query -- comma separated
    @return: The DAG run we get from the DB

    Args:
        run_ids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['RunLogOutWithRun']
    """

    return sync_detailed(
        run_ids=run_ids,
        client=client,
    ).parsed


async def asyncio_detailed(
    run_ids: str,
    *,
    client: AuthenticatedClient,
) -> Response[List["RunLogOutWithRun"]]:
    """Get Runs

     Bulk queries run IDs. This will return a list of runs, in the same order as the run IDs.

    @param request:
    @param run_ids: The DAG run ID to query -- comma separated
    @return: The DAG run we get from the DB

    Args:
        run_ids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['RunLogOutWithRun']]
    """

    kwargs = _get_kwargs(
        run_ids=run_ids,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    run_ids: str,
    *,
    client: AuthenticatedClient,
) -> Optional[List["RunLogOutWithRun"]]:
    """Get Runs

     Bulk queries run IDs. This will return a list of runs, in the same order as the run IDs.

    @param request:
    @param run_ids: The DAG run ID to query -- comma separated
    @return: The DAG run we get from the DB

    Args:
        run_ids (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['RunLogOutWithRun']
    """

    return (
        await asyncio_detailed(
            run_ids=run_ids,
            client=client,
        )
    ).parsed
