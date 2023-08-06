from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance


T = TypeVar("T", bound="BrakeStatus")


@attr.s(auto_attribs=True)
class BrakeStatus:
    """
    Attributes:
        brake_fluid (Union[Unset, RInstance]):
    """

    brake_fluid: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        brake_fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.brake_fluid, Unset):
            brake_fluid = self.brake_fluid.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if brake_fluid is not UNSET:
            field_dict["brakeFluid"] = brake_fluid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance

        d = src_dict.copy()
        _brake_fluid = d.pop("brakeFluid", UNSET)
        brake_fluid: Union[Unset, RInstance]
        if isinstance(_brake_fluid, Unset):
            brake_fluid = UNSET
        else:
            brake_fluid = RInstance.from_dict(_brake_fluid)

        brake_status = cls(
            brake_fluid=brake_fluid,
        )

        brake_status.additional_properties = d
        return brake_status

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
