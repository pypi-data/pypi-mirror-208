from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance


T = TypeVar("T", bound="WarningVals")


@attr.s(auto_attribs=True)
class WarningVals:
    """
    Attributes:
        bulb_failure (Union[Unset, RInstance]):
    """

    bulb_failure: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bulb_failure: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.bulb_failure, Unset):
            bulb_failure = self.bulb_failure.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bulb_failure is not UNSET:
            field_dict["bulbFailure"] = bulb_failure

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance

        d = src_dict.copy()
        _bulb_failure = d.pop("bulbFailure", UNSET)
        bulb_failure: Union[Unset, RInstance]
        if isinstance(_bulb_failure, Unset):
            bulb_failure = UNSET
        else:
            bulb_failure = RInstance.from_dict(_bulb_failure)

        warning_vals = cls(
            bulb_failure=bulb_failure,
        )

        warning_vals.additional_properties = d
        return warning_vals

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
