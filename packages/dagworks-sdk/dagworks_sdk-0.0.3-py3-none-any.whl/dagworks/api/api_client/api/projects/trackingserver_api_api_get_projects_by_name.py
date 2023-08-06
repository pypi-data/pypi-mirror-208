from http import HTTPStatus
from typing import Any, Dict, List, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_out import ProjectOut
from ...types import Response


def _get_kwargs(
    project_name: str,
    *,
    client: AuthenticatedClient,
) -> Dict[str, Any]:
    url = "{}/api/v0/projects/by_name/{project_name}".format(
        client.base_url, project_name=project_name
    )

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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[List["ProjectOut"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProjectOut.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[List["ProjectOut"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[List["ProjectOut"]]:
    r"""Get Projects By Name

     Gets a project by name. Note that this doesn't use the standard auth mechanism,
    as a user could see a \"subset\" of projects by name. So we do the auth check manually
    in the loop below. A little inefficient, but this will be fine for now.

    @param request: Django request
    @param project_name:
    @return: Null if project does not exist, else the project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ProjectOut']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[List["ProjectOut"]]:
    r"""Get Projects By Name

     Gets a project by name. Note that this doesn't use the standard auth mechanism,
    as a user could see a \"subset\" of projects by name. So we do the auth check manually
    in the loop below. A little inefficient, but this will be fine for now.

    @param request: Django request
    @param project_name:
    @return: Null if project does not exist, else the project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ProjectOut']
    """

    return sync_detailed(
        project_name=project_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[List["ProjectOut"]]:
    r"""Get Projects By Name

     Gets a project by name. Note that this doesn't use the standard auth mechanism,
    as a user could see a \"subset\" of projects by name. So we do the auth check manually
    in the loop below. A little inefficient, but this will be fine for now.

    @param request: Django request
    @param project_name:
    @return: Null if project does not exist, else the project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ProjectOut']]
    """

    kwargs = _get_kwargs(
        project_name=project_name,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[List["ProjectOut"]]:
    r"""Get Projects By Name

     Gets a project by name. Note that this doesn't use the standard auth mechanism,
    as a user could see a \"subset\" of projects by name. So we do the auth check manually
    in the loop below. A little inefficient, but this will be fine for now.

    @param request: Django request
    @param project_name:
    @return: Null if project does not exist, else the project

    Args:
        project_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ProjectOut']
    """

    return (
        await asyncio_detailed(
            project_name=project_name,
            client=client,
        )
    ).parsed
