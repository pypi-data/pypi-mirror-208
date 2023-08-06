from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...models.run_wait_result_script_by_path_json_body import RunWaitResultScriptByPathJsonBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace: str,
    path: str,
    *,
    client: Client,
    json_body: RunWaitResultScriptByPathJsonBody,
    parent_job: Union[Unset, None, str] = UNSET,
    job_id: Union[Unset, None, str] = UNSET,
    include_header: Union[Unset, None, str] = UNSET,
    queue_limit: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/w/{workspace}/jobs/run_wait_result/p/{path}".format(client.base_url, workspace=workspace, path=path)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["parent_job"] = parent_job

    params["job_id"] = job_id

    params["include_header"] = include_header

    params["queue_limit"] = queue_limit

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
    path: str,
    *,
    client: Client,
    json_body: RunWaitResultScriptByPathJsonBody,
    parent_job: Union[Unset, None, str] = UNSET,
    job_id: Union[Unset, None, str] = UNSET,
    include_header: Union[Unset, None, str] = UNSET,
    queue_limit: Union[Unset, None, str] = UNSET,
) -> Response[Any]:
    """run script by path

    Args:
        workspace (str):
        path (str):
        parent_job (Union[Unset, None, str]):
        job_id (Union[Unset, None, str]):
        include_header (Union[Unset, None, str]):
        queue_limit (Union[Unset, None, str]):
        json_body (RunWaitResultScriptByPathJsonBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        path=path,
        client=client,
        json_body=json_body,
        parent_job=parent_job,
        job_id=job_id,
        include_header=include_header,
        queue_limit=queue_limit,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    workspace: str,
    path: str,
    *,
    client: Client,
    json_body: RunWaitResultScriptByPathJsonBody,
    parent_job: Union[Unset, None, str] = UNSET,
    job_id: Union[Unset, None, str] = UNSET,
    include_header: Union[Unset, None, str] = UNSET,
    queue_limit: Union[Unset, None, str] = UNSET,
) -> Response[Any]:
    """run script by path

    Args:
        workspace (str):
        path (str):
        parent_job (Union[Unset, None, str]):
        job_id (Union[Unset, None, str]):
        include_header (Union[Unset, None, str]):
        queue_limit (Union[Unset, None, str]):
        json_body (RunWaitResultScriptByPathJsonBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        workspace=workspace,
        path=path,
        client=client,
        json_body=json_body,
        parent_job=parent_job,
        job_id=job_id,
        include_header=include_header,
        queue_limit=queue_limit,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)
