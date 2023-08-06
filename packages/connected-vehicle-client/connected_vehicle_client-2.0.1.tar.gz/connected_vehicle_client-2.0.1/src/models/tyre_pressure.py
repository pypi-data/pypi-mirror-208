from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance


T = TypeVar("T", bound="TyrePressure")


@attr.s(auto_attribs=True)
class TyrePressure:
    """
    Attributes:
        front_left (Union[Unset, RInstance]):
        front_right (Union[Unset, RInstance]):
        rear_left (Union[Unset, RInstance]):
        rear_right (Union[Unset, RInstance]):
    """

    front_left: Union[Unset, "RInstance"] = UNSET
    front_right: Union[Unset, "RInstance"] = UNSET
    rear_left: Union[Unset, "RInstance"] = UNSET
    rear_right: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        front_left: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.front_left, Unset):
            front_left = self.front_left.to_dict()

        front_right: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.front_right, Unset):
            front_right = self.front_right.to_dict()

        rear_left: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rear_left, Unset):
            rear_left = self.rear_left.to_dict()

        rear_right: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rear_right, Unset):
            rear_right = self.rear_right.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if front_left is not UNSET:
            field_dict["frontLeft"] = front_left
        if front_right is not UNSET:
            field_dict["frontRight"] = front_right
        if rear_left is not UNSET:
            field_dict["rearLeft"] = rear_left
        if rear_right is not UNSET:
            field_dict["rearRight"] = rear_right

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance

        d = src_dict.copy()
        _front_left = d.pop("frontLeft", UNSET)
        front_left: Union[Unset, RInstance]
        if isinstance(_front_left, Unset):
            front_left = UNSET
        else:
            front_left = RInstance.from_dict(_front_left)

        _front_right = d.pop("frontRight", UNSET)
        front_right: Union[Unset, RInstance]
        if isinstance(_front_right, Unset):
            front_right = UNSET
        else:
            front_right = RInstance.from_dict(_front_right)

        _rear_left = d.pop("rearLeft", UNSET)
        rear_left: Union[Unset, RInstance]
        if isinstance(_rear_left, Unset):
            rear_left = UNSET
        else:
            rear_left = RInstance.from_dict(_rear_left)

        _rear_right = d.pop("rearRight", UNSET)
        rear_right: Union[Unset, RInstance]
        if isinstance(_rear_right, Unset):
            rear_right = UNSET
        else:
            rear_right = RInstance.from_dict(_rear_right)

        tyre_pressure = cls(
            front_left=front_left,
            front_right=front_right,
            rear_left=rear_left,
            rear_right=rear_right,
        )

        tyre_pressure.additional_properties = d
        return tyre_pressure

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
