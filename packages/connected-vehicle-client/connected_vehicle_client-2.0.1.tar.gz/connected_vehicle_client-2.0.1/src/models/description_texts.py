from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="DescriptionTexts")


@attr.s(auto_attribs=True)
class DescriptionTexts:
    """
    Attributes:
        model (Union[Unset, str]):
        upholstery (Union[Unset, str]):
        steering (Union[Unset, str]):
    """

    model: Union[Unset, str] = UNSET
    upholstery: Union[Unset, str] = UNSET
    steering: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model = self.model
        upholstery = self.upholstery
        steering = self.steering

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model is not UNSET:
            field_dict["model"] = model
        if upholstery is not UNSET:
            field_dict["upholstery"] = upholstery
        if steering is not UNSET:
            field_dict["steering"] = steering

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        model = d.pop("model", UNSET)

        upholstery = d.pop("upholstery", UNSET)

        steering = d.pop("steering", UNSET)

        description_texts = cls(
            model=model,
            upholstery=upholstery,
            steering=steering,
        )

        description_texts.additional_properties = d
        return description_texts

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
