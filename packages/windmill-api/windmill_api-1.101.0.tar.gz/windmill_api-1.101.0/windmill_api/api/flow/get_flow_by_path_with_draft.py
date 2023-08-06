from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.get_flow_by_path_with_draft_response_200 import GetFlowByPathWithDraftResponse200
from ...types import Response


def _get_kwargs(
    workspace: str,
    path: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/flows/get/draft/{path}".format(client.base_url, workspace=workspace, path=path)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[GetFlowByPathWithDraftResponse200]:
    if response.status_code == 200:
        response_200 = GetFlowByPathWithDraftResponse200.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[GetFlowByPathWithDraftResponse200]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    workspace: str,
    path: str,
    *,
    client: Client,
) -> Response[GetFlowByPathWithDraftResponse200]:
    """get flow by path with draft

    Args:
        workspace (str):
        path (str):

    Returns:
        Response[GetFlowByPathWithDraftResponse200]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        path=path,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    workspace: str,
    path: str,
    *,
    client: Client,
) -> Optional[GetFlowByPathWithDraftResponse200]:
    """get flow by path with draft

    Args:
        workspace (str):
        path (str):

    Returns:
        Response[GetFlowByPathWithDraftResponse200]
    """

    return sync_detailed(
        workspace=workspace,
        path=path,
        client=client,
    ).parsed


async def asyncio_detailed(
    workspace: str,
    path: str,
    *,
    client: Client,
) -> Response[GetFlowByPathWithDraftResponse200]:
    """get flow by path with draft

    Args:
        workspace (str):
        path (str):

    Returns:
        Response[GetFlowByPathWithDraftResponse200]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        path=path,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    workspace: str,
    path: str,
    *,
    client: Client,
) -> Optional[GetFlowByPathWithDraftResponse200]:
    """get flow by path with draft

    Args:
        workspace (str):
        path (str):

    Returns:
        Response[GetFlowByPathWithDraftResponse200]
    """

    return (
        await asyncio_detailed(
            workspace=workspace,
            path=path,
            client=client,
        )
    ).parsed
