from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    algo: Union[Unset, None, str] = "md5",
    foreign_key: Union[None, Unset, int, str] = UNSET,
    uri: Union[Unset, None, str] = UNSET,
    metadata: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/exact/hash/{collection_name}/uri".format(client.base_url, collection_name=collection_name)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["algo"] = algo

    json_foreign_key: Union[None, Unset, int, str]
    if isinstance(foreign_key, Unset):
        json_foreign_key = UNSET
    elif foreign_key is None:
        json_foreign_key = None

    else:
        json_foreign_key = foreign_key

    params["foreign_key"] = json_foreign_key

    params["uri"] = uri

    params["metadata"] = metadata

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = cast(Any, response.json())
        return response_200
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    algo: Union[Unset, None, str] = "md5",
    foreign_key: Union[None, Unset, int, str] = UNSET,
    uri: Union[Unset, None, str] = UNSET,
    metadata: Union[Unset, None, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Put Entry By Uri

    Args:
        collection_name (str):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        foreign_key (Union[None, Unset, int, str]):
        uri (Union[Unset, None, str]):
        metadata (Union[Unset, None, str]):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        client=client,
        algo=algo,
        foreign_key=foreign_key,
        uri=uri,
        metadata=metadata,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    algo: Union[Unset, None, str] = "md5",
    foreign_key: Union[None, Unset, int, str] = UNSET,
    uri: Union[Unset, None, str] = UNSET,
    metadata: Union[Unset, None, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Put Entry By Uri

    Args:
        collection_name (str):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        foreign_key (Union[None, Unset, int, str]):
        uri (Union[Unset, None, str]):
        metadata (Union[Unset, None, str]):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    return sync_detailed(
        collection_name=collection_name,
        client=client,
        algo=algo,
        foreign_key=foreign_key,
        uri=uri,
        metadata=metadata,
    ).parsed


async def asyncio_detailed(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    algo: Union[Unset, None, str] = "md5",
    foreign_key: Union[None, Unset, int, str] = UNSET,
    uri: Union[Unset, None, str] = UNSET,
    metadata: Union[Unset, None, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Put Entry By Uri

    Args:
        collection_name (str):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        foreign_key (Union[None, Unset, int, str]):
        uri (Union[Unset, None, str]):
        metadata (Union[Unset, None, str]):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        client=client,
        algo=algo,
        foreign_key=foreign_key,
        uri=uri,
        metadata=metadata,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    algo: Union[Unset, None, str] = "md5",
    foreign_key: Union[None, Unset, int, str] = UNSET,
    uri: Union[Unset, None, str] = UNSET,
    metadata: Union[Unset, None, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Put Entry By Uri

    Args:
        collection_name (str):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        foreign_key (Union[None, Unset, int, str]):
        uri (Union[Unset, None, str]):
        metadata (Union[Unset, None, str]):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    return (
        await asyncio_detailed(
            collection_name=collection_name,
            client=client,
            algo=algo,
            foreign_key=foreign_key,
            uri=uri,
            metadata=metadata,
        )
    ).parsed
