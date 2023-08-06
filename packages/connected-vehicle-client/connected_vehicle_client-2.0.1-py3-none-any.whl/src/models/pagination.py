from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Pagination")


@attr.s(auto_attribs=True)
class Pagination:
    """
    Attributes:
        previous (Union[Unset, str]):
        next_ (Union[Unset, str]):
        limit (Union[Unset, int]):
    """

    previous: Union[Unset, str] = UNSET
    next_: Union[Unset, str] = UNSET
    limit: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        previous = self.previous
        next_ = self.next_
        limit = self.limit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if previous is not UNSET:
            field_dict["previous"] = previous
        if next_ is not UNSET:
            field_dict["next"] = next_
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        previous = d.pop("previous", UNSET)

        next_ = d.pop("next", UNSET)

        limit = d.pop("limit", UNSET)

        pagination = cls(
            previous=previous,
            next_=next_,
            limit=limit,
        )

        pagination.additional_properties = d
        return pagination

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
