from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_out import ProjectOut
from ...models.trackingserver_api_api_update_project_body_params import (
    TrackingserverApiApiUpdateProjectBodyParams,
)
from ...types import Response


def _get_kwargs(
    project_id: int,
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiUpdateProjectBodyParams,
) -> Dict[str, Any]:
    url = "{}/api/v0/project/{project_id}".format(client.base_url, project_id=project_id)

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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[ProjectOut]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ProjectOut.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[ProjectOut]:
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
    json_body: TrackingserverApiApiUpdateProjectBodyParams,
) -> Response[ProjectOut]:
    """Update Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project_id: The project id
    @param project: Project to create
    @param visibility: Visibility object of the project
    @param documentation: Documentation asset  list-- will be attached to the project
    @return: The updated project

    Args:
        project_id (int):
        json_body (TrackingserverApiApiUpdateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectOut]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
        json_body=json_body,
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
    json_body: TrackingserverApiApiUpdateProjectBodyParams,
) -> Optional[ProjectOut]:
    """Update Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project_id: The project id
    @param project: Project to create
    @param visibility: Visibility object of the project
    @param documentation: Documentation asset  list-- will be attached to the project
    @return: The updated project

    Args:
        project_id (int):
        json_body (TrackingserverApiApiUpdateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectOut
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    project_id: int,
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiUpdateProjectBodyParams,
) -> Response[ProjectOut]:
    """Update Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project_id: The project id
    @param project: Project to create
    @param visibility: Visibility object of the project
    @param documentation: Documentation asset  list-- will be attached to the project
    @return: The updated project

    Args:
        project_id (int):
        json_body (TrackingserverApiApiUpdateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectOut]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: int,
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiUpdateProjectBodyParams,
) -> Optional[ProjectOut]:
    """Update Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project_id: The project id
    @param project: Project to create
    @param visibility: Visibility object of the project
    @param documentation: Documentation asset  list-- will be attached to the project
    @return: The updated project

    Args:
        project_id (int):
        json_body (TrackingserverApiApiUpdateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectOut
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
