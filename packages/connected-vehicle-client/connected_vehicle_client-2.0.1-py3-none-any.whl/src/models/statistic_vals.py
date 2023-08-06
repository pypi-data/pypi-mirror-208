from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="StatisticVals")


@attr.s(auto_attribs=True)
class StatisticVals:
    """
    Attributes:
        average_speed (Union[Unset, RInstanceWithUnit]):
        distance_to_empty (Union[Unset, RInstanceWithUnit]):
        trip_meter_1 (Union[Unset, RInstanceWithUnit]):
        trip_meter_2 (Union[Unset, RInstanceWithUnit]):
        average_fuel_consumption (Union[Unset, RInstanceWithUnit]):
    """

    average_speed: Union[Unset, "RInstanceWithUnit"] = UNSET
    distance_to_empty: Union[Unset, "RInstanceWithUnit"] = UNSET
    trip_meter_1: Union[Unset, "RInstanceWithUnit"] = UNSET
    trip_meter_2: Union[Unset, "RInstanceWithUnit"] = UNSET
    average_fuel_consumption: Union[Unset, "RInstanceWithUnit"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        average_speed: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.average_speed, Unset):
            average_speed = self.average_speed.to_dict()

        distance_to_empty: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.distance_to_empty, Unset):
            distance_to_empty = self.distance_to_empty.to_dict()

        trip_meter_1: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.trip_meter_1, Unset):
            trip_meter_1 = self.trip_meter_1.to_dict()

        trip_meter_2: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.trip_meter_2, Unset):
            trip_meter_2 = self.trip_meter_2.to_dict()

        average_fuel_consumption: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.average_fuel_consumption, Unset):
            average_fuel_consumption = self.average_fuel_consumption.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if average_speed is not UNSET:
            field_dict["averageSpeed"] = average_speed
        if distance_to_empty is not UNSET:
            field_dict["distanceToEmpty"] = distance_to_empty
        if trip_meter_1 is not UNSET:
            field_dict["tripMeter1"] = trip_meter_1
        if trip_meter_2 is not UNSET:
            field_dict["tripMeter2"] = trip_meter_2
        if average_fuel_consumption is not UNSET:
            field_dict["averageFuelConsumption"] = average_fuel_consumption

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _average_speed = d.pop("averageSpeed", UNSET)
        average_speed: Union[Unset, RInstanceWithUnit]
        if isinstance(_average_speed, Unset):
            average_speed = UNSET
        else:
            average_speed = RInstanceWithUnit.from_dict(_average_speed)

        _distance_to_empty = d.pop("distanceToEmpty", UNSET)
        distance_to_empty: Union[Unset, RInstanceWithUnit]
        if isinstance(_distance_to_empty, Unset):
            distance_to_empty = UNSET
        else:
            distance_to_empty = RInstanceWithUnit.from_dict(_distance_to_empty)

        _trip_meter_1 = d.pop("tripMeter1", UNSET)
        trip_meter_1: Union[Unset, RInstanceWithUnit]
        if isinstance(_trip_meter_1, Unset):
            trip_meter_1 = UNSET
        else:
            trip_meter_1 = RInstanceWithUnit.from_dict(_trip_meter_1)

        _trip_meter_2 = d.pop("tripMeter2", UNSET)
        trip_meter_2: Union[Unset, RInstanceWithUnit]
        if isinstance(_trip_meter_2, Unset):
            trip_meter_2 = UNSET
        else:
            trip_meter_2 = RInstanceWithUnit.from_dict(_trip_meter_2)

        _average_fuel_consumption = d.pop("averageFuelConsumption", UNSET)
        average_fuel_consumption: Union[Unset, RInstanceWithUnit]
        if isinstance(_average_fuel_consumption, Unset):
            average_fuel_consumption = UNSET
        else:
            average_fuel_consumption = RInstanceWithUnit.from_dict(_average_fuel_consumption)

        statistic_vals = cls(
            average_speed=average_speed,
            distance_to_empty=distance_to_empty,
            trip_meter_1=trip_meter_1,
            trip_meter_2=trip_meter_2,
            average_fuel_consumption=average_fuel_consumption,
        )

        statistic_vals.additional_properties = d
        return statistic_vals

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
