from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.run_log_in import RunLogIn
from ...models.run_log_out import RunLogOut
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    json_body: RunLogIn,
    project_version_id: int,
) -> Dict[str, Any]:
    url = "{}/api/v0/runs/".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["project_version_id"] = project_version_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[RunLogOut]:
    if response.status_code == HTTPStatus.OK:
        response_200 = RunLogOut.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[RunLogOut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: RunLogIn,
    project_version_id: int,
) -> Response[RunLogOut]:
    """Log Run

     Logs a DAG run

    @param project_version_id: The project version ID to log the run for
    @param dag_run: The DAG run to log
    @return: The DAG run we get from the DB

    Args:
        project_version_id (int):
        json_body (RunLogIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RunLogOut]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        project_version_id=project_version_id,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    json_body: RunLogIn,
    project_version_id: int,
) -> Optional[RunLogOut]:
    """Log Run

     Logs a DAG run

    @param project_version_id: The project version ID to log the run for
    @param dag_run: The DAG run to log
    @return: The DAG run we get from the DB

    Args:
        project_version_id (int):
        json_body (RunLogIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RunLogOut
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        project_version_id=project_version_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: RunLogIn,
    project_version_id: int,
) -> Response[RunLogOut]:
    """Log Run

     Logs a DAG run

    @param project_version_id: The project version ID to log the run for
    @param dag_run: The DAG run to log
    @return: The DAG run we get from the DB

    Args:
        project_version_id (int):
        json_body (RunLogIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RunLogOut]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        project_version_id=project_version_id,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: RunLogIn,
    project_version_id: int,
) -> Optional[RunLogOut]:
    """Log Run

     Logs a DAG run

    @param project_version_id: The project version ID to log the run for
    @param dag_run: The DAG run to log
    @return: The DAG run we get from the DB

    Args:
        project_version_id (int):
        json_body (RunLogIn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RunLogOut
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            project_version_id=project_version_id,
        )
    ).parsed
