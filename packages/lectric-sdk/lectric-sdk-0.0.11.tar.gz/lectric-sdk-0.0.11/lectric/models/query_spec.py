from typing import *

import attr

from ..models.query_spec_object_type import QuerySpecObjectType
from ..types import UNSET, Unset

T = TypeVar("T", bound="QuerySpec")


def unset_if_none(_dict: dict, key: Any) -> Union[Any, Unset]:
    if key not in _dict or _dict[key] is None:
        return UNSET
    return _dict[key]


@attr.s(auto_attribs=True)
class QuerySpec:
    """
    Attributes:
        expr (str):
        collection_name (str):
        object_type (Union[Unset, QuerySpecObjectType]):  Default: QuerySpecObjectType.QUERYSPEC.
        output_fields (Union[Unset, List[str]]):
        partitions (Union[Unset, List[str]]):
        timeout (Union[Unset, float]):
    """

    expr: str
    collection_name: str
    object_type: Union[Unset, QuerySpecObjectType] = QuerySpecObjectType.QUERYSPEC
    output_fields: Union[Unset, List[str]] = UNSET
    partitions: Union[Unset, List[str]] = UNSET
    timeout: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __init__(
        self,
        expr: str,
        collection_name: str,
        object_type: Union[Unset, QuerySpecObjectType] = QuerySpecObjectType.QUERYSPEC,
        output_fields: Union[Unset, List[str]] = UNSET,
        partitions: Union[Unset, List[str]] = UNSET,
        timeout: Union[Unset, float] = UNSET,
    ):
        """ """

        self.expr = expr
        self.collection_name = collection_name
        self.object_type = object_type
        self.output_fields = output_fields
        self.partitions = partitions
        self.timeout = timeout

    def to_dict(self) -> Dict[str, Any]:
        expr = self.expr
        collection_name = self.collection_name
        object_type: Union[Unset, str] = UNSET
        if not isinstance(self.object_type, Unset):
            object_type = self.object_type.value

        output_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.output_fields, Unset):
            output_fields = self.output_fields

        partitions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.partitions, Unset):
            partitions = self.partitions

        timeout = self.timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "expr": expr,
                "collection_name": collection_name,
            }
        )
        if object_type is not UNSET:
            field_dict["object_type"] = object_type
        if output_fields is not UNSET:
            field_dict["output_fields"] = output_fields
        if partitions is not UNSET:
            field_dict["partitions"] = partitions
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        expr = d.pop("expr")

        collection_name = d.pop("collection_name")

        _object_type = unset_if_none(d, "object_type")
        object_type: Union[Unset, QuerySpecObjectType]
        if isinstance(_object_type, Unset):
            object_type = UNSET
        else:
            object_type = QuerySpecObjectType(_object_type)

        output_fields = cast(List[str], unset_if_none(d, "output_fields"))

        partitions = cast(List[str], unset_if_none(d, "partitions"))

        timeout = unset_if_none(d, "timeout")

        query_spec = cls(
            expr=expr,
            collection_name=collection_name,
            object_type=object_type,
            output_fields=output_fields,
            partitions=partitions,
            timeout=timeout,
        )

        query_spec.additional_properties = d
        return query_spec

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
