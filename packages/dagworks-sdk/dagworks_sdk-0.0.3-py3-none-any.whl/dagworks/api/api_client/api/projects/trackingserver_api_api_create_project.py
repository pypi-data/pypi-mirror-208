from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.project_out import ProjectOut
from ...models.trackingserver_api_api_create_project_body_params import (
    TrackingserverApiApiCreateProjectBodyParams,
)
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiCreateProjectBodyParams,
) -> Dict[str, Any]:
    url = "{}/api/v0/projects".format(client.base_url)

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
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiCreateProjectBodyParams,
) -> Response[ProjectOut]:
    """Create Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project: Project to create
    @param documentation: Documentation asset -- will be attached to the project
    @param exists_ok: Whether or not its OK if the project already exists
    @param project:
    @return:

    Args:
        json_body (TrackingserverApiApiCreateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectOut]
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
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiCreateProjectBodyParams,
) -> Optional[ProjectOut]:
    """Create Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project: Project to create
    @param documentation: Documentation asset -- will be attached to the project
    @param exists_ok: Whether or not its OK if the project already exists
    @param project:
    @return:

    Args:
        json_body (TrackingserverApiApiCreateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectOut
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiCreateProjectBodyParams,
) -> Response[ProjectOut]:
    """Create Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project: Project to create
    @param documentation: Documentation asset -- will be attached to the project
    @param exists_ok: Whether or not its OK if the project already exists
    @param project:
    @return:

    Args:
        json_body (TrackingserverApiApiCreateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ProjectOut]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: TrackingserverApiApiCreateProjectBodyParams,
) -> Optional[ProjectOut]:
    """Create Project

     Creates a project. User specifies visibility -- it will always be user-visible.

    @param request: Request from django ninja
    @param project: Project to create
    @param documentation: Documentation asset -- will be attached to the project
    @param exists_ok: Whether or not its OK if the project already exists
    @param project:
    @return:

    Args:
        json_body (TrackingserverApiApiCreateProjectBodyParams):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ProjectOut
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
