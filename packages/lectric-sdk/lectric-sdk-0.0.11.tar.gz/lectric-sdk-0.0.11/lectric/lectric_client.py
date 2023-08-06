from typing import Dict, List, Union
import json
import os
from requests import Response
from functools import wraps

from .models.input_data import InputData
from .models.index_in_spec import IndexInSpec
from .models.collection import Collection
from .models.collection_in_spec import CollectionInSpec
from .models.query_spec import QuerySpec
from .models.vector_query_spec import VectorQuerySpec
from .models.query_response import QueryResponse

from .helpers import *
from .client import AuthenticatedClient
from .types import File as fastAPIFile


# defaults
from .api.default import  root_get, root_auth_auth_get, list_connections_connections_get

# collections
from .api.collection import (
    create_collection_collection_create_post,
    exists_collection_collection_exists_name_get,
    is_empty_collection_collection_empty_name_get,
    get_collection_collection_get_name_get,
    list_collections_collection_list_get,
    get_indexes_collection_indexes_name_get,
    drop_collection_collection_delete,
    sizeof_collection_collection_size_name_get,
    delete_entities_collection_entities_delete,
    sample_collection_sample_get
)

# ingest
from .api.ingest import ingest_ingest_post

# index
from .api.index import create_index_create_post, delete_index_collection_name_field_name_delete

# query
from .api.query import query_query_fields_post, query_query_vectors_post

# exact
from .api.exact import (
    create_collection_exact_create_collection_post,
    put_entry_by_uri_exact_hash_collection_name_uri_put,
    put_entry_by_file_exact_hash_collection_name_file_put,
    lookup_by_uri_exact_lookup_hash_uri_collection_name_get,
    lookup_by_file_exact_lookup_file_collection_name_post,
    list_collections_exact_list_get,
    delete_collections_exact_collection_delete,
    get_available_algos_exact_algos_get,
    is_algo_available_exact_available_algo_get,
    info_exact_info_get
)

from .models.body_put_entry_by_file_exact_hash_collection_name_file_put import BodyPutEntryByFileExactHashCollectionNameFilePut
from .models.body_lookup_by_file_exact_lookup_file_collection_name_post import BodyLookupByFileExactLookupFileCollectionNamePost


def propagate_exception(func):
    @wraps(func)
    def propagator(*args, **kwargs):

        response = func(*args, **kwargs)

        if response.status_code == HTTPStatus.OK:
            return response.parsed
        else:
            raise RuntimeError(f"HTTP Code: {response.status_code}, {response}")

    return propagator


class LectricClient:

    def __init__(self, api_url: str, api_key: str=None,
                    cookies: Dict[str, str]={}, timeout:int=60000) -> None:
        """The Lectric client class

        Args:
            api_url (str): The base url for the api service
            api_key (str, optional): The API key for the service. Defaults to None.
            cookies (Dict[str, str], optional): Optional cookies to be maintained. Defaults to {}.
            timeout (int, optional): Request timeout. Defaults to 60000.
        """
        self.api_url = api_url

        self.client = AuthenticatedClient(base_url=self.api_url,
                                    token=api_key, cookies=cookies,
                                    headers={"X-API-KEY": api_key} if api_key else {},
                                    timeout=timeout)

        response_dict = json.loads(self.verify_connection(api_key is not None).content)

        self.api_build_id = response_dict.get("lectric-build-id")
        self.backend_db = response_dict.get("lectric-vdb-backend")

    def verify_connection(self, is_authenticated: bool=False) -> Response:
        """Test the connection to the Lectric server

        Returns:
            bool|RuntimeError: Either True for success or failure
        """

        if is_authenticated:
            response = root_auth_auth_get.sync_detailed(client=self.client)
        else:
            response = root_get.sync_detailed(client=self.client)

        if response.status_code != HTTPStatus.OK.value:
            raise RuntimeError(f"HTTP Code: {response.status_code}, {response}")

        return response

    @propagate_exception
    def list_connections(self) -> List[str]:
        """List the connections created within the vector db

        Returns:
            List[str]: A list of the connection names
        """
        return list_connections_connections_get.sync_detailed(client=self.client)


    ########################## collections ###############################

    @propagate_exception
    def create_collection(self, coll_in_spec: CollectionInSpec) -> Collection:
        """Create an exact OR vector collection. If `coll_in_spec.approx == True` then the collection
            created will be a vector/approximate collection; if not it will be an exact one 

        Args:
            coll_in_spec (CollectionInSpec): The collection specification to be created

        Returns:
            Collection: An object representing the created collection
        """
        if coll_in_spec.approx:
            return create_collection_collection_create_post.sync_detailed(client=self.client, json_body=coll_in_spec)
        return create_collection_exact_create_collection_post.sync_detailed(client=self.client, json_body=coll_in_spec)


    @propagate_exception
    def collection_exists(self, name: str, exact: bool=False) -> bool:
        """Check if a collection exists

        Args:
            name (str): The name of the collection
            exact (bool): Looking for an exact colletion?

        Returns:
            bool: True if the collection exist, else False
        """
        return exists_collection_collection_exists_name_get.sync_detailed(client=self.client, name=name, exact=exact)


    @propagate_exception
    def is_collection_empty(self, name: str) -> bool:
        """Check if the collection has data or is empty

        Args:
            name (str): The name of the collection

        Returns:
            bool: True if the collection is empty, else False
        """
        return is_empty_collection_collection_empty_name_get.sync_detailed(client=self.client, name=name)


    @propagate_exception
    def get_collection(self, name: str) -> Collection:
        """Get a collection by name. Each collection has a unique, user defined name

        Args:
            name (str): The name of the collection.

        Returns:
            Collection: A representation of the collection
        """
        return get_collection_collection_get_name_get.sync_detailed(client=self.client, name=name)


    @propagate_exception
    def get_indexes(self, collection_name: str) -> List[str]:
        """Get a list of the field names for which indexes are defined

        Args:
            collection_name (str): The name of the collection for which indexes are queried

        Returns:
            List[str]: A list of the field names for which indexes are defined
        """
        return get_indexes_collection_indexes_name_get.sync_detailed(client=self.client, name=collection_name)


    @propagate_exception
    def list_collections(self, exact_only: bool=False) -> List[str]:
        """List the names of the collections

        Returns:
            List[str]: The collection names
        """
        if exact_only:
            res = list_collections_exact_list_get.sync_detailed(client=self.client)
            return res
        return list_collections_collection_list_get.sync_detailed(client=self.client)


    @propagate_exception
    def drop_collection(self, name: str, exact: bool=False) -> None:
        """Drop (delete) a collection by name

        Args:
            name (str): The name of the collection to be dropped
            exact (bool): The collection is exact

        Returns:
            _type_: None
        """
        if exact:
            return delete_collections_exact_collection_delete.sync_detailed(client=self.client, name=name)
        return drop_collection_collection_delete.sync_detailed(client=self.client, name=name)


    @propagate_exception
    def delete_entities(self, collection_name: str,
                ids: Union[List[str], List[int]]) -> None:
        """Delete entities by Primary key ID

        Args:
            collection_name (str): The collection name
            ids (Union[List[str], List[int]]): The list of IDs for which is to happen

        Returns:
            _type_: None
        """
        return delete_entities_collection_entities_delete.sync_detailed(
                client=self.client, name=collection_name, json_body=ids)


    @propagate_exception
    def sample_entities(self, collection_name: str, max_samples: int = 20):
        """Sample entities of a collection

        Args:
            collection_name (str): The collection name
            max_samples (int, optional): The maximum number of entities to sample. Defaults to 20.

        Returns:
            _type_: _description_
        """

        return sample_collection_sample_get.sync_detailed(client=self.client,
                collection_name=collection_name, max_samples=max_samples)


    @propagate_exception
    def sizeof(self, name: str, exact: bool=False) -> int:
        """Get the size of (number of entities) in a collection

        Args:
            name (str): The collection name
            exact (bool): is the collection an exact lookup?

        Raises:
            RuntimeError: If collection does not exist

        Returns:
            int: The size of the collection
        """
        return sizeof_collection_collection_size_name_get.sync_detailed(client=self.client, name=name, exact=exact)


    @propagate_exception
    def ingest(self, data: InputData) -> None:
        """Ingest data into a collection

        Args:
            data (InputData): The data to be ingested

        Returns:
            _type_: None
        """
        return ingest_ingest_post.sync_detailed(client=self.client, json_body=data)

    @propagate_exception
    def create_index(self, index_spec: IndexInSpec) -> None:
        """Create an index for one field within the collection

        Args:
            index_spec (IndexInSpec): The creation spec of the index

        Returns:
            _type_: None
        """
        return create_index_create_post.sync_detailed(client=self.client, json_body=index_spec)


    @propagate_exception
    def drop_index(self, collection_name: str, field_name: str) -> None:
        """Drop (delete) a previously created index

        Args:
            collection_name (str): The collection name
            field_name (str): The field name on which the index is defined

        Returns:
            _type_: None
        """
        return delete_index_collection_name_field_name_delete.sync_detailed(client=self.client, collection_name=collection_name, field_name=field_name)

    @propagate_exception
    def query(self, query_spec: Union[QuerySpec, VectorQuerySpec]) -> Union[List[Dict], QueryResponse]:
        """Query a collection using either a vector, a batch of vectors or query on the fields

        Args:
            query_spec (Union[QuerySpec, VectorQuerySpec]): The specification of the query

        Raises:
            RuntimeError: If the query spec is non conformant, this is raised.

        Returns:
            Union[List[Dict], QueryResponse]: Either a list with the queried fields or a QueryResponse object from a vector query
        """

        if isinstance(query_spec, QuerySpec):
            return query_query_fields_post.sync_detailed(client=self.client, json_body=query_spec)
        elif isinstance(query_spec, VectorQuerySpec):
            return query_query_vectors_post.sync_detailed(client=self.client, json_body=query_spec)
        else:
            raise RuntimeError(f"Unable to query with given query spec of type {type(query_spec)}")

    @propagate_exception
    def put_exact(self, collection_name: str,
                    foreign_key: Union[str, int]=None,
                    algo: str="md5",
                    file: Union[str, bytes, BinaryIO]=None,
                    uri: str=None,
                    metadata: str=None) -> str:
        """Put an entry into an exact store collection

        Args:
            collection_name (str): The collection name
            foreign_key (Union[str, int], optional): Foreign key
            algo (str, optional): The hashing algorithm to use. Defaults to "md5".
            file (Union[str, bytes, BinaryIO], optional): The file containing the data. Defaults to None.
            uri (str, optional): The URI of input data. Defaults to None.
            metadata (str, optional): Additional metadata to store with entry

        Raises:
            RuntimeError: When input file or URI is unprocessable 

        Returns:
            str: The inserted hash
        """

        if uri:
            return put_entry_by_uri_exact_hash_collection_name_uri_put.sync_detailed(
                collection_name=collection_name, client=self.client,
                foreign_key=foreign_key, uri=uri, algo=algo, metadata=metadata
            )
        elif file:

            if is_file_like(file):
                tmp_file = file
            elif isinstance(file, str):
                if not os.path.exists(file):
                    raise RuntimeError("`file` arg as str must be the path to file")
                tmp_file = open(file, "rb")

            elif isinstance(file, bytes): # Assume encoded JPG
                tmp_file = to_tmpfile(file)
            else:
                raise RuntimeError("Unable to process `file` argument, unsupported input type")

            return put_entry_by_file_exact_hash_collection_name_file_put.sync_detailed(
                collection_name=collection_name, client=self.client,
                multipart_data=BodyPutEntryByFileExactHashCollectionNameFilePut(
                        file=fastAPIFile(payload=tmp_file, file_name="tmpfile", mime_type="image/jpg")
                    ), foreign_key = foreign_key, algo=algo, metadata=metadata
                )

    @propagate_exception
    def lookup_exact(self, collection_name: str,
                    algo: str = "md5",
                    file: Union[str, bytes, BinaryIO]=None, uri: str=None) -> Union[List[str], None]:
        """Lookup exact entry in a collection

        Args:
            collection_name (str): The name of the collection
            algo (str, optional): The hash algorithm to use (Should match insertion hashing algorithm). Defaults to "md5".
            file (Union[str, bytes, BinaryIO], optional): Input file data. Defaults to None.
            uri (str, optional): Input URI data. Defaults to None.

        Raises:
            RuntimeError: When input file or URI is unprocessable

        Returns:
            Union[List[str], None]: The found match or None
        """
        if uri:
            return lookup_by_uri_exact_lookup_hash_uri_collection_name_get.sync_detailed(
                collection_name=collection_name, client=self.client, uri=uri, algo=algo
            )
        elif file:
            if is_file_like(file):
                tmp_file = file
            elif isinstance(file, str):
                if not os.path.exists(file):
                    raise RuntimeError("`file` arg as str must be the path to file")
                tmp_file = open(file, "rb")

            elif isinstance(file, bytes): # Assume encoded JPG
                tmp_file = to_tmpfile(file)
            else:
                raise RuntimeError("Unable to process `file` argument, unsupported input type")

            return lookup_by_file_exact_lookup_file_collection_name_post.sync_detailed(
                collection_name=collection_name, client=self.client, algo=algo,
                multipart_data=BodyLookupByFileExactLookupFileCollectionNamePost(
                        file=fastAPIFile(payload=tmp_file, file_name="tmpfile", mime_type="image/jpg")
                    )
                )

    @propagate_exception
    def get_exact_hash_algos(self) -> List[str]:
        """Get a list of the available hashing algorithms

        Returns:
            List[str]: A list of the hash algos
        """
        return get_available_algos_exact_algos_get.sync_detailed(client=self.client)

    @propagate_exception
    def is_exact_algos_available(self, algo: str) -> bool:
        """Determine whether a specific hashing algorithm is supported

        Args:
            algo (str): The algorithm name

        Returns:
            bool: True if the algorithm is supported/available for use
        """
        return is_algo_available_exact_available_algo_get.sync_detailed(client=self.client)
        
    def _pformat_collection(self, collection: Collection) -> str:
        return f"""
                Collection name: {collection.name}
                Size (estimated): {self.sizeof(collection.name)}
                Index(es): {self.get_indexes(collection.name)}
                {pformat_collection_schema(collection.coll_schema)}
                """
    @propagate_exception
    def _exact_info(self, collection_name: str):
         return info_exact_info_get.sync_detailed(client=self.client, name=collection_name)

    
    def info(self, collection_name: str, exact: bool = False) -> str:
        """Get info on a collection

        Args:
            collection_name (str): The unique name of the collection
            exact (bool, ojptional): Exact collections only? Defaults to False.
        """
        if exact:
            return self._exact_info(collection_name)
        else:
            return self._pformat_collection(self.get_collection(collection_name))