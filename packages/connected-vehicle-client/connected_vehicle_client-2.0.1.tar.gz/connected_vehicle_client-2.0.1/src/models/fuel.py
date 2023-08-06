from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="Fuel")


@attr.s(auto_attribs=True)
class Fuel:
    """
    Attributes:
        fuel_amount (Union[Unset, RInstanceWithUnit]):
    """

    fuel_amount: Union[Unset, "RInstanceWithUnit"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        fuel_amount: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fuel_amount, Unset):
            fuel_amount = self.fuel_amount.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fuel_amount is not UNSET:
            field_dict["fuelAmount"] = fuel_amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _fuel_amount = d.pop("fuelAmount", UNSET)
        fuel_amount: Union[Unset, RInstanceWithUnit]
        if isinstance(_fuel_amount, Unset):
            fuel_amount = UNSET
        else:
            fuel_amount = RInstanceWithUnit.from_dict(_fuel_amount)

        fuel = cls(
            fuel_amount=fuel_amount,
        )

        fuel.additional_properties = d
        return fuel

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
