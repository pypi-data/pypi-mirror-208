import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommandAccessibility")


@attr.s(auto_attribs=True)
class CommandAccessibility:
    """
    Attributes:
        accessible (Union[Unset, bool]):
        accessible_until (Union[Unset, datetime.datetime]):
    """

    accessible: Union[Unset, bool] = UNSET
    accessible_until: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        accessible = self.accessible
        accessible_until: Union[Unset, str] = UNSET
        if not isinstance(self.accessible_until, Unset):
            accessible_until = self.accessible_until.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accessible is not UNSET:
            field_dict["accessible"] = accessible
        if accessible_until is not UNSET:
            field_dict["accessibleUntil"] = accessible_until

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        accessible = d.pop("accessible", UNSET)

        _accessible_until = d.pop("accessibleUntil", UNSET)
        accessible_until: Union[Unset, datetime.datetime]
        if isinstance(_accessible_until, Unset):
            accessible_until = UNSET
        else:
            accessible_until = isoparse(_accessible_until)

        command_accessibility = cls(
            accessible=accessible,
            accessible_until=accessible_until,
        )

        command_accessibility.additional_properties = d
        return command_accessibility

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
