from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.description_texts import DescriptionTexts
    from ..models.vehicle_images import VehicleImages


T = TypeVar("T", bound="VehicleMetadata")


@attr.s(auto_attribs=True)
class VehicleMetadata:
    """
    Attributes:
        model_year (Union[Unset, str]):
        vin (Union[Unset, str]):
        external_colour (Union[Unset, str]):
        images (Union[Unset, VehicleImages]):
        descriptions (Union[Unset, DescriptionTexts]):
    """

    model_year: Union[Unset, str] = UNSET
    vin: Union[Unset, str] = UNSET
    external_colour: Union[Unset, str] = UNSET
    images: Union[Unset, "VehicleImages"] = UNSET
    descriptions: Union[Unset, "DescriptionTexts"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model_year = self.model_year
        vin = self.vin
        external_colour = self.external_colour
        images: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.images, Unset):
            images = self.images.to_dict()

        descriptions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.descriptions, Unset):
            descriptions = self.descriptions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model_year is not UNSET:
            field_dict["modelYear"] = model_year
        if vin is not UNSET:
            field_dict["vin"] = vin
        if external_colour is not UNSET:
            field_dict["externalColour"] = external_colour
        if images is not UNSET:
            field_dict["images"] = images
        if descriptions is not UNSET:
            field_dict["descriptions"] = descriptions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.description_texts import DescriptionTexts
        from ..models.vehicle_images import VehicleImages

        d = src_dict.copy()
        model_year = d.pop("modelYear", UNSET)

        vin = d.pop("vin", UNSET)

        external_colour = d.pop("externalColour", UNSET)

        _images = d.pop("images", UNSET)
        images: Union[Unset, VehicleImages]
        if isinstance(_images, Unset):
            images = UNSET
        else:
            images = VehicleImages.from_dict(_images)

        _descriptions = d.pop("descriptions", UNSET)
        descriptions: Union[Unset, DescriptionTexts]
        if isinstance(_descriptions, Unset):
            descriptions = UNSET
        else:
            descriptions = DescriptionTexts.from_dict(_descriptions)

        vehicle_metadata = cls(
            model_year=model_year,
            vin=vin,
            external_colour=external_colour,
            images=images,
            descriptions=descriptions,
        )

        vehicle_metadata.additional_properties = d
        return vehicle_metadata

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
