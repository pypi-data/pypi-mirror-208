from http import HTTPStatus
import tempfile
import requests
import numpy as np
from typing import BinaryIO, List, Any
import io
from .models.collection import Collection
from .models.collection_schema import CollectionSchema
from .models.field_schema import FieldSchema


def create_random_vectors(nvects: int, dim: int) -> List[List[float]]:
    return [np.random.rand(dim).tolist() for _ in range(nvects)]

def check_ok(resp: requests.Response):
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(resp.json())

def is_file_like(obj: Any) -> bool:
    """Does the object appear to be a file?

    Args:
        obj (Any): The object in question

    Returns:
        [bool]: True if is file like else False
    """
    return isinstance(obj, io.TextIOBase) or \
                isinstance(obj, io.BufferedIOBase) or \
                isinstance(obj, io.RawIOBase) or \
                isinstance(obj, io.IOBase)


def to_tmpfile(_input: bytes) -> BinaryIO:
    """Write a sequence of bytes a temporary file

    Args:
        _input (bytes): The data to be written to temp file

    Returns:
        [BinaryIO]: The temporary file that is closed when garbage collectede
    """
    fp = tempfile.TemporaryFile()
    fp.write(_input)
    fp.seek(0)
    return fp

def pformat_field_schema(fschema: FieldSchema) -> str:
    desc = "" if not fschema.description else f"Description: {fschema.description}"
    dim = "" if not fschema.dim else f"Dim: {fschema.dim}"
    max_len = "" if not fschema.max_length else f"Max length: {fschema.max_length}"
    s =  f"""
            FieldSchema:
                Name: {fschema.name}
                {desc}
                Type: {fschema.dtype}
                Primary key: {fschema.is_primary}
                Auto ID: {bool(fschema.auto_id)}
                {dim}
                {max_len}
        """.rstrip()

    return s

def pformat_collection_schema(cschema: CollectionSchema) -> str:
    schema_str: str = "\nCollectionSchema:"
    schema_str += "" if not cschema.description else f"\n\tDescription: {cschema.description}"
    for field in cschema.fields:
        field_str = pformat_field_schema(field)
        schema_str += field_str
    return schema_str
