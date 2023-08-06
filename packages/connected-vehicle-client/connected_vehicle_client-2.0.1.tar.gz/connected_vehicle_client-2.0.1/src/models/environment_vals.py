from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="EnvironmentVals")


@attr.s(auto_attribs=True)
class EnvironmentVals:
    """
    Attributes:
        external_temp (Union[Unset, RInstanceWithUnit]):
    """

    external_temp: Union[Unset, "RInstanceWithUnit"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        external_temp: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.external_temp, Unset):
            external_temp = self.external_temp.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_temp is not UNSET:
            field_dict["externalTemp"] = external_temp

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _external_temp = d.pop("externalTemp", UNSET)
        external_temp: Union[Unset, RInstanceWithUnit]
        if isinstance(_external_temp, Unset):
            external_temp = UNSET
        else:
            external_temp = RInstanceWithUnit.from_dict(_external_temp)

        environment_vals = cls(
            external_temp=external_temp,
        )

        environment_vals.additional_properties = d
        return environment_vals

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
