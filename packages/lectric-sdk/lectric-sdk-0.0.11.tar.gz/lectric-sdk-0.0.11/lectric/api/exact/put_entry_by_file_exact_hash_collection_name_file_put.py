from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient
from ...models.body_put_entry_by_file_exact_hash_collection_name_file_put import (
    BodyPutEntryByFileExactHashCollectionNameFilePut,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    multipart_data: BodyPutEntryByFileExactHashCollectionNameFilePut,
    foreign_key: Union[int, str],
    algo: Union[Unset, None, str] = "md5",
    metadata: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/exact/hash/{collection_name}/file".format(client.base_url, collection_name=collection_name)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}

    json_foreign_key = foreign_key

    params["foreign_key"] = json_foreign_key

    params["algo"] = algo

    params["metadata"] = metadata

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
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
    multipart_data: BodyPutEntryByFileExactHashCollectionNameFilePut,
    foreign_key: Union[int, str],
    algo: Union[Unset, None, str] = "md5",
    metadata: Union[Unset, None, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Put Entry By File

    Args:
        collection_name (str):
        foreign_key (Union[int, str]):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        metadata (Union[Unset, None, str]):
        multipart_data (BodyPutEntryByFileExactHashCollectionNameFilePut):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        client=client,
        multipart_data=multipart_data,
        foreign_key=foreign_key,
        algo=algo,
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
    multipart_data: BodyPutEntryByFileExactHashCollectionNameFilePut,
    foreign_key: Union[int, str],
    algo: Union[Unset, None, str] = "md5",
    metadata: Union[Unset, None, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Put Entry By File

    Args:
        collection_name (str):
        foreign_key (Union[int, str]):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        metadata (Union[Unset, None, str]):
        multipart_data (BodyPutEntryByFileExactHashCollectionNameFilePut):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    return sync_detailed(
        collection_name=collection_name,
        client=client,
        multipart_data=multipart_data,
        foreign_key=foreign_key,
        algo=algo,
        metadata=metadata,
    ).parsed


async def asyncio_detailed(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    multipart_data: BodyPutEntryByFileExactHashCollectionNameFilePut,
    foreign_key: Union[int, str],
    algo: Union[Unset, None, str] = "md5",
    metadata: Union[Unset, None, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Put Entry By File

    Args:
        collection_name (str):
        foreign_key (Union[int, str]):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        metadata (Union[Unset, None, str]):
        multipart_data (BodyPutEntryByFileExactHashCollectionNameFilePut):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        collection_name=collection_name,
        client=client,
        multipart_data=multipart_data,
        foreign_key=foreign_key,
        algo=algo,
        metadata=metadata,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    collection_name: str,
    *,
    client: AuthenticatedClient,
    multipart_data: BodyPutEntryByFileExactHashCollectionNameFilePut,
    foreign_key: Union[int, str],
    algo: Union[Unset, None, str] = "md5",
    metadata: Union[Unset, None, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Put Entry By File

    Args:
        collection_name (str):
        foreign_key (Union[int, str]):
        algo (Union[Unset, None, str]):  Default: 'md5'.
        metadata (Union[Unset, None, str]):
        multipart_data (BodyPutEntryByFileExactHashCollectionNameFilePut):

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    return (
        await asyncio_detailed(
            collection_name=collection_name,
            client=client,
            multipart_data=multipart_data,
            foreign_key=foreign_key,
            algo=algo,
            metadata=metadata,
        )
    ).parsed
