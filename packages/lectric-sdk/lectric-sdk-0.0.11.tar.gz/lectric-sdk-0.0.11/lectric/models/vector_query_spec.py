from typing import *

import attr

from ..models.query_params import QueryParams
from ..models.vector_query_spec_object_type import VectorQuerySpecObjectType
from ..types import UNSET, Unset

T = TypeVar("T", bound="VectorQuerySpec")


def unset_if_none(_dict: dict, key: Any) -> Union[Any, Unset]:
    if key not in _dict or _dict[key] is None:
        return UNSET
    return _dict[key]


@attr.s(auto_attribs=True)
class VectorQuerySpec:
    """
    Attributes:
        data (List[List[Any]]):
        collection_name (str):
        search_field (str):
        search_params (QueryParams):
        limit (int):
        object_type (Union[Unset, VectorQuerySpecObjectType]):  Default: VectorQuerySpecObjectType.VECTORQUERYSPEC.
        output_fields (Union[Unset, List[str]]):
        expr (Union[Unset, str]):
        partitions (Union[Unset, List[str]]):
        timeout (Union[Unset, float]):
        round_decimal (Union[Unset, int]):  Default: -1.
    """

    data: List[List[Any]]
    collection_name: str
    search_field: str
    search_params: QueryParams
    limit: int
    object_type: Union[Unset, VectorQuerySpecObjectType] = VectorQuerySpecObjectType.VECTORQUERYSPEC
    output_fields: Union[Unset, List[str]] = UNSET
    expr: Union[Unset, str] = UNSET
    partitions: Union[Unset, List[str]] = UNSET
    timeout: Union[Unset, float] = UNSET
    round_decimal: Union[Unset, int] = -1
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __init__(
        self,
        data: List[List[Any]],
        collection_name: str,
        search_field: str,
        search_params: QueryParams,
        limit: int,
        object_type: Union[Unset, VectorQuerySpecObjectType] = VectorQuerySpecObjectType.VECTORQUERYSPEC,
        output_fields: Union[Unset, List[str]] = UNSET,
        expr: Union[Unset, str] = UNSET,
        partitions: Union[Unset, List[str]] = UNSET,
        timeout: Union[Unset, float] = UNSET,
        round_decimal: Union[Unset, int] = -1,
    ):
        """ """

        self.data = data
        self.collection_name = collection_name
        self.search_field = search_field
        self.search_params = search_params
        self.limit = limit
        self.object_type = object_type
        self.output_fields = output_fields
        self.expr = expr
        self.partitions = partitions
        self.timeout = timeout
        self.round_decimal = round_decimal

    def to_dict(self) -> Dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data

            data.append(data_item)

        collection_name = self.collection_name
        search_field = self.search_field
        search_params = self.search_params.to_dict()

        limit = self.limit
        object_type: Union[Unset, str] = UNSET
        if not isinstance(self.object_type, Unset):
            object_type = self.object_type.value

        output_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.output_fields, Unset):
            output_fields = self.output_fields

        expr = self.expr
        partitions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.partitions, Unset):
            partitions = self.partitions

        timeout = self.timeout
        round_decimal = self.round_decimal

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "collection_name": collection_name,
                "search_field": search_field,
                "search_params": search_params,
                "limit": limit,
            }
        )
        if object_type is not UNSET:
            field_dict["object_type"] = object_type
        if output_fields is not UNSET:
            field_dict["output_fields"] = output_fields
        if expr is not UNSET:
            field_dict["expr"] = expr
        if partitions is not UNSET:
            field_dict["partitions"] = partitions
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if round_decimal is not UNSET:
            field_dict["round_decimal"] = round_decimal

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = cast(List[Any], data_item_data)

            data.append(data_item)

        collection_name = d.pop("collection_name")

        search_field = d.pop("search_field")

        search_params = QueryParams.from_dict(d.pop("search_params"))

        limit = d.pop("limit")

        _object_type = unset_if_none(d, "object_type")
        object_type: Union[Unset, VectorQuerySpecObjectType]
        if isinstance(_object_type, Unset):
            object_type = UNSET
        else:
            object_type = VectorQuerySpecObjectType(_object_type)

        output_fields = cast(List[str], unset_if_none(d, "output_fields"))

        expr = unset_if_none(d, "expr")

        partitions = cast(List[str], unset_if_none(d, "partitions"))

        timeout = unset_if_none(d, "timeout")

        round_decimal = unset_if_none(d, "round_decimal")

        vector_query_spec = cls(
            data=data,
            collection_name=collection_name,
            search_field=search_field,
            search_params=search_params,
            limit=limit,
            object_type=object_type,
            output_fields=output_fields,
            expr=expr,
            partitions=partitions,
            timeout=timeout,
            round_decimal=round_decimal,
        )

        vector_query_spec.additional_properties = d
        return vector_query_spec

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
