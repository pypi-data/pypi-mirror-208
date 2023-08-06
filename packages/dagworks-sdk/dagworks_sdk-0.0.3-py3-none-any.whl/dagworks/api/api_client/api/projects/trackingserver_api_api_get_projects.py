from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paged_project_out import PagedProjectOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Dict[str, Any]:
    url = "{}/api/v0/projects".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[PagedProjectOut]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PagedProjectOut.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[PagedProjectOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Response[PagedProjectOut]:
    """Get Projects

     Gets a list of projects visible by a user, auto-paginating.
    TODO -- fix to use actual pagination on the db side

    @param request:
    @return: A list of projects

    Args:
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedProjectOut]
    """

    kwargs = _get_kwargs(
        client=client,
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
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Optional[PagedProjectOut]:
    """Get Projects

     Gets a list of projects visible by a user, auto-paginating.
    TODO -- fix to use actual pagination on the db side

    @param request:
    @return: A list of projects

    Args:
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedProjectOut
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Response[PagedProjectOut]:
    """Get Projects

     Gets a list of projects visible by a user, auto-paginating.
    TODO -- fix to use actual pagination on the db side

    @param request:
    @return: A list of projects

    Args:
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedProjectOut]
    """

    kwargs = _get_kwargs(
        client=client,
        limit=limit,
        offset=offset,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    limit: Union[Unset, None, int] = 100,
    offset: Union[Unset, None, int] = 0,
) -> Optional[PagedProjectOut]:
    """Get Projects

     Gets a list of projects visible by a user, auto-paginating.
    TODO -- fix to use actual pagination on the db side

    @param request:
    @return: A list of projects

    Args:
        limit (Union[Unset, None, int]):  Default: 100.
        offset (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedProjectOut
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed
