from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="EngineDiagnosticVals")


@attr.s(auto_attribs=True)
class EngineDiagnosticVals:
    """
    Attributes:
        engine_coolant_level (Union[Unset, RInstance]):
        oil_level (Union[Unset, RInstance]):
        oil_pressure (Union[Unset, RInstance]):
        engine_coolant_temp (Union[Unset, RInstanceWithUnit]):
    """

    engine_coolant_level: Union[Unset, "RInstance"] = UNSET
    oil_level: Union[Unset, "RInstance"] = UNSET
    oil_pressure: Union[Unset, "RInstance"] = UNSET
    engine_coolant_temp: Union[Unset, "RInstanceWithUnit"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        engine_coolant_level: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_coolant_level, Unset):
            engine_coolant_level = self.engine_coolant_level.to_dict()

        oil_level: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.oil_level, Unset):
            oil_level = self.oil_level.to_dict()

        oil_pressure: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.oil_pressure, Unset):
            oil_pressure = self.oil_pressure.to_dict()

        engine_coolant_temp: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_coolant_temp, Unset):
            engine_coolant_temp = self.engine_coolant_temp.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if engine_coolant_level is not UNSET:
            field_dict["engineCoolantLevel"] = engine_coolant_level
        if oil_level is not UNSET:
            field_dict["oilLevel"] = oil_level
        if oil_pressure is not UNSET:
            field_dict["oilPressure"] = oil_pressure
        if engine_coolant_temp is not UNSET:
            field_dict["engineCoolantTemp"] = engine_coolant_temp

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _engine_coolant_level = d.pop("engineCoolantLevel", UNSET)
        engine_coolant_level: Union[Unset, RInstance]
        if isinstance(_engine_coolant_level, Unset):
            engine_coolant_level = UNSET
        else:
            engine_coolant_level = RInstance.from_dict(_engine_coolant_level)

        _oil_level = d.pop("oilLevel", UNSET)
        oil_level: Union[Unset, RInstance]
        if isinstance(_oil_level, Unset):
            oil_level = UNSET
        else:
            oil_level = RInstance.from_dict(_oil_level)

        _oil_pressure = d.pop("oilPressure", UNSET)
        oil_pressure: Union[Unset, RInstance]
        if isinstance(_oil_pressure, Unset):
            oil_pressure = UNSET
        else:
            oil_pressure = RInstance.from_dict(_oil_pressure)

        _engine_coolant_temp = d.pop("engineCoolantTemp", UNSET)
        engine_coolant_temp: Union[Unset, RInstanceWithUnit]
        if isinstance(_engine_coolant_temp, Unset):
            engine_coolant_temp = UNSET
        else:
            engine_coolant_temp = RInstanceWithUnit.from_dict(_engine_coolant_temp)

        engine_diagnostic_vals = cls(
            engine_coolant_level=engine_coolant_level,
            oil_level=oil_level,
            oil_pressure=oil_pressure,
            engine_coolant_temp=engine_coolant_temp,
        )

        engine_diagnostic_vals.additional_properties = d
        return engine_diagnostic_vals

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
