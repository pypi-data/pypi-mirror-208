from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="Odometer")


@attr.s(auto_attribs=True)
class Odometer:
    """
    Attributes:
        odometer (Union[Unset, RInstanceWithUnit]):
    """

    odometer: Union[Unset, "RInstanceWithUnit"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        odometer: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.odometer, Unset):
            odometer = self.odometer.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if odometer is not UNSET:
            field_dict["odometer"] = odometer

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _odometer = d.pop("odometer", UNSET)
        odometer: Union[Unset, RInstanceWithUnit]
        if isinstance(_odometer, Unset):
            odometer = UNSET
        else:
            odometer = RInstanceWithUnit.from_dict(_odometer)

        odometer = cls(
            odometer=odometer,
        )

        odometer.additional_properties = d
        return odometer

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
