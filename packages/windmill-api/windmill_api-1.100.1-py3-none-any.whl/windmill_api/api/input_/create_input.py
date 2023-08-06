from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...models.create_input_json_body import CreateInputJsonBody
from ...models.create_input_runnable_type import CreateInputRunnableType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace: str,
    *,
    client: Client,
    json_body: CreateInputJsonBody,
    runnable_id: Union[Unset, None, str] = UNSET,
    runnable_type: Union[Unset, None, CreateInputRunnableType] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/inputs/create".format(client.base_url, workspace=workspace)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["runnable_id"] = runnable_id

    json_runnable_type: Union[Unset, None, str] = UNSET
    if not isinstance(runnable_type, Unset):
        json_runnable_type = runnable_type.value if runnable_type else None

    params["runnable_type"] = json_runnable_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    workspace: str,
    *,
    client: Client,
    json_body: CreateInputJsonBody,
    runnable_id: Union[Unset, None, str] = UNSET,
    runnable_type: Union[Unset, None, CreateInputRunnableType] = UNSET,
) -> Response[Any]:
    """Create an Input for future use in a script or flow

    Args:
        workspace (str):
        runnable_id (Union[Unset, None, str]):
        runnable_type (Union[Unset, None, CreateInputRunnableType]):
        json_body (CreateInputJsonBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        client=client,
        json_body=json_body,
        runnable_id=runnable_id,
        runnable_type=runnable_type,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    workspace: str,
    *,
    client: Client,
    json_body: CreateInputJsonBody,
    runnable_id: Union[Unset, None, str] = UNSET,
    runnable_type: Union[Unset, None, CreateInputRunnableType] = UNSET,
) -> Response[Any]:
    """Create an Input for future use in a script or flow

    Args:
        workspace (str):
        runnable_id (Union[Unset, None, str]):
        runnable_type (Union[Unset, None, CreateInputRunnableType]):
        json_body (CreateInputJsonBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        client=client,
        json_body=json_body,
        runnable_id=runnable_id,
        runnable_type=runnable_type,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)
