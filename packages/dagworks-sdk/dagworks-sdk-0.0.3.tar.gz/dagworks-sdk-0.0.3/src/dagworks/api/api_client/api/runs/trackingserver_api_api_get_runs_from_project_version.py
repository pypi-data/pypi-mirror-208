from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paged_run_log_out import PagedRunLogOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    project_version_id: int,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Dict[str, Any]:
    url = "{}/api/v0/runs/by_project_version".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["project_version_id"] = project_version_id

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "params": params,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[PagedRunLogOut]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PagedRunLogOut.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[PagedRunLogOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    project_version_id: int,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Response[PagedRunLogOut]:
    """Get Runs From Project Version

     Gets a list of DAG runs for a project version

    @param request:
    @param project_version_id: The project version ID to query
    @return: A list of DAG runs associated with that project version ID, paginated

    Args:
        project_version_id (int):
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedRunLogOut]
    """

    kwargs = _get_kwargs(
        client=client,
        project_version_id=project_version_id,
        limit=limit,
        offset=offset,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    project_version_id: int,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Optional[PagedRunLogOut]:
    """Get Runs From Project Version

     Gets a list of DAG runs for a project version

    @param request:
    @param project_version_id: The project version ID to query
    @return: A list of DAG runs associated with that project version ID, paginated

    Args:
        project_version_id (int):
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedRunLogOut
    """

    return sync_detailed(
        client=client,
        project_version_id=project_version_id,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    project_version_id: int,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Response[PagedRunLogOut]:
    """Get Runs From Project Version

     Gets a list of DAG runs for a project version

    @param request:
    @param project_version_id: The project version ID to query
    @return: A list of DAG runs associated with that project version ID, paginated

    Args:
        project_version_id (int):
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedRunLogOut]
    """

    kwargs = _get_kwargs(
        client=client,
        project_version_id=project_version_id,
        limit=limit,
        offset=offset,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    project_version_id: int,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Optional[PagedRunLogOut]:
    """Get Runs From Project Version

     Gets a list of DAG runs for a project version

    @param request:
    @param project_version_id: The project version ID to query
    @return: A list of DAG runs associated with that project version ID, paginated

    Args:
        project_version_id (int):
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedRunLogOut
    """

    return (
        await asyncio_detailed(
            client=client,
            project_version_id=project_version_id,
            limit=limit,
            offset=offset,
        )
    ).parsed
