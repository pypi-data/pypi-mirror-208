from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_version_out import ProjectVersionOut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: int,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, None, str] = UNSET,
    git_hash: Union[Unset, None, str] = UNSET,
    git_repo: Union[Unset, None, str] = UNSET,
    include_archived: Union[Unset, None, bool] = False,
) -> Dict[str, Any]:
    url = "{}/api/v0/project_versions/{project_id}".format(client.base_url, project_id=project_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["name"] = name

    params["git_hash"] = git_hash

    params["git_repo"] = git_repo

    params["include_archived"] = include_archived

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


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[List["ProjectVersionOut"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectVersionOut.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[List["ProjectVersionOut"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, None, str] = UNSET,
    git_hash: Union[Unset, None, str] = UNSET,
    git_repo: Union[Unset, None, str] = UNSET,
    include_archived: Union[Unset, None, bool] = False,
) -> Response[List["ProjectVersionOut"]]:
    """Get Project Versions

     Gets a list of project versions for a project.
    At some point soon we'll likely need to paginate this...

    @param git_repo:
    @param git_hash:
    @param request:
    @param project_id: The project ID to query
    @return: A list of project versions associated with that project ID, paginated

    Args:
        project_id (int):
        name (Union[Unset, None, str]):
        git_hash (Union[Unset, None, str]):
        git_repo (Union[Unset, None, str]):
        include_archived (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ProjectVersionOut']]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
        name=name,
        git_hash=git_hash,
        git_repo=git_repo,
        include_archived=include_archived,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: int,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, None, str] = UNSET,
    git_hash: Union[Unset, None, str] = UNSET,
    git_repo: Union[Unset, None, str] = UNSET,
    include_archived: Union[Unset, None, bool] = False,
) -> Optional[List["ProjectVersionOut"]]:
    """Get Project Versions

     Gets a list of project versions for a project.
    At some point soon we'll likely need to paginate this...

    @param git_repo:
    @param git_hash:
    @param request:
    @param project_id: The project ID to query
    @return: A list of project versions associated with that project ID, paginated

    Args:
        project_id (int):
        name (Union[Unset, None, str]):
        git_hash (Union[Unset, None, str]):
        git_repo (Union[Unset, None, str]):
        include_archived (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ProjectVersionOut']
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        name=name,
        git_hash=git_hash,
        git_repo=git_repo,
        include_archived=include_archived,
    ).parsed


async def asyncio_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, None, str] = UNSET,
    git_hash: Union[Unset, None, str] = UNSET,
    git_repo: Union[Unset, None, str] = UNSET,
    include_archived: Union[Unset, None, bool] = False,
) -> Response[List["ProjectVersionOut"]]:
    """Get Project Versions

     Gets a list of project versions for a project.
    At some point soon we'll likely need to paginate this...

    @param git_repo:
    @param git_hash:
    @param request:
    @param project_id: The project ID to query
    @return: A list of project versions associated with that project ID, paginated

    Args:
        project_id (int):
        name (Union[Unset, None, str]):
        git_hash (Union[Unset, None, str]):
        git_repo (Union[Unset, None, str]):
        include_archived (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ProjectVersionOut']]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
        name=name,
        git_hash=git_hash,
        git_repo=git_repo,
        include_archived=include_archived,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: int,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, None, str] = UNSET,
    git_hash: Union[Unset, None, str] = UNSET,
    git_repo: Union[Unset, None, str] = UNSET,
    include_archived: Union[Unset, None, bool] = False,
) -> Optional[List["ProjectVersionOut"]]:
    """Get Project Versions

     Gets a list of project versions for a project.
    At some point soon we'll likely need to paginate this...

    @param git_repo:
    @param git_hash:
    @param request:
    @param project_id: The project ID to query
    @return: A list of project versions associated with that project ID, paginated

    Args:
        project_id (int):
        name (Union[Unset, None, str]):
        git_hash (Union[Unset, None, str]):
        git_repo (Union[Unset, None, str]):
        include_archived (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ProjectVersionOut']
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            name=name,
            git_hash=git_hash,
            git_repo=git_repo,
            include_archived=include_archived,
        )
    ).parsed
