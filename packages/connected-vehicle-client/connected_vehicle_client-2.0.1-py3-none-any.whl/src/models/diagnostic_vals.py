from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance
    from ..models.r_instance_with_unit import RInstanceWithUnit


T = TypeVar("T", bound="DiagnosticVals")


@attr.s(auto_attribs=True)
class DiagnosticVals:
    """
    Attributes:
        engine_hours_to_service (Union[Unset, RInstance]):
        km_to_service (Union[Unset, RInstanceWithUnit]):
        main_battery_status (Union[Unset, RInstance]):
        months_to_service (Union[Unset, RInstance]):
        service_type (Union[Unset, RInstance]):
        service_status (Union[Unset, RInstance]):
        service_trigger (Union[Unset, RInstance]):
        backup_battery_remaining (Union[Unset, RInstance]):
        washer_fluid_level (Union[Unset, RInstance]):
    """

    engine_hours_to_service: Union[Unset, "RInstance"] = UNSET
    km_to_service: Union[Unset, "RInstanceWithUnit"] = UNSET
    main_battery_status: Union[Unset, "RInstance"] = UNSET
    months_to_service: Union[Unset, "RInstance"] = UNSET
    service_type: Union[Unset, "RInstance"] = UNSET
    service_status: Union[Unset, "RInstance"] = UNSET
    service_trigger: Union[Unset, "RInstance"] = UNSET
    backup_battery_remaining: Union[Unset, "RInstance"] = UNSET
    washer_fluid_level: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        engine_hours_to_service: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_hours_to_service, Unset):
            engine_hours_to_service = self.engine_hours_to_service.to_dict()

        km_to_service: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.km_to_service, Unset):
            km_to_service = self.km_to_service.to_dict()

        main_battery_status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.main_battery_status, Unset):
            main_battery_status = self.main_battery_status.to_dict()

        months_to_service: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.months_to_service, Unset):
            months_to_service = self.months_to_service.to_dict()

        service_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.service_type, Unset):
            service_type = self.service_type.to_dict()

        service_status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.service_status, Unset):
            service_status = self.service_status.to_dict()

        service_trigger: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.service_trigger, Unset):
            service_trigger = self.service_trigger.to_dict()

        backup_battery_remaining: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.backup_battery_remaining, Unset):
            backup_battery_remaining = self.backup_battery_remaining.to_dict()

        washer_fluid_level: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.washer_fluid_level, Unset):
            washer_fluid_level = self.washer_fluid_level.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if engine_hours_to_service is not UNSET:
            field_dict["engineHoursToService"] = engine_hours_to_service
        if km_to_service is not UNSET:
            field_dict["kmToService"] = km_to_service
        if main_battery_status is not UNSET:
            field_dict["mainBatteryStatus"] = main_battery_status
        if months_to_service is not UNSET:
            field_dict["monthsToService"] = months_to_service
        if service_type is not UNSET:
            field_dict["serviceType"] = service_type
        if service_status is not UNSET:
            field_dict["serviceStatus"] = service_status
        if service_trigger is not UNSET:
            field_dict["serviceTrigger"] = service_trigger
        if backup_battery_remaining is not UNSET:
            field_dict["backupBatteryRemaining"] = backup_battery_remaining
        if washer_fluid_level is not UNSET:
            field_dict["washerFluidLevel"] = washer_fluid_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance
        from ..models.r_instance_with_unit import RInstanceWithUnit

        d = src_dict.copy()
        _engine_hours_to_service = d.pop("engineHoursToService", UNSET)
        engine_hours_to_service: Union[Unset, RInstance]
        if isinstance(_engine_hours_to_service, Unset):
            engine_hours_to_service = UNSET
        else:
            engine_hours_to_service = RInstance.from_dict(_engine_hours_to_service)

        _km_to_service = d.pop("kmToService", UNSET)
        km_to_service: Union[Unset, RInstanceWithUnit]
        if isinstance(_km_to_service, Unset):
            km_to_service = UNSET
        else:
            km_to_service = RInstanceWithUnit.from_dict(_km_to_service)

        _main_battery_status = d.pop("mainBatteryStatus", UNSET)
        main_battery_status: Union[Unset, RInstance]
        if isinstance(_main_battery_status, Unset):
            main_battery_status = UNSET
        else:
            main_battery_status = RInstance.from_dict(_main_battery_status)

        _months_to_service = d.pop("monthsToService", UNSET)
        months_to_service: Union[Unset, RInstance]
        if isinstance(_months_to_service, Unset):
            months_to_service = UNSET
        else:
            months_to_service = RInstance.from_dict(_months_to_service)

        _service_type = d.pop("serviceType", UNSET)
        service_type: Union[Unset, RInstance]
        if isinstance(_service_type, Unset):
            service_type = UNSET
        else:
            service_type = RInstance.from_dict(_service_type)

        _service_status = d.pop("serviceStatus", UNSET)
        service_status: Union[Unset, RInstance]
        if isinstance(_service_status, Unset):
            service_status = UNSET
        else:
            service_status = RInstance.from_dict(_service_status)

        _service_trigger = d.pop("serviceTrigger", UNSET)
        service_trigger: Union[Unset, RInstance]
        if isinstance(_service_trigger, Unset):
            service_trigger = UNSET
        else:
            service_trigger = RInstance.from_dict(_service_trigger)

        _backup_battery_remaining = d.pop("backupBatteryRemaining", UNSET)
        backup_battery_remaining: Union[Unset, RInstance]
        if isinstance(_backup_battery_remaining, Unset):
            backup_battery_remaining = UNSET
        else:
            backup_battery_remaining = RInstance.from_dict(_backup_battery_remaining)

        _washer_fluid_level = d.pop("washerFluidLevel", UNSET)
        washer_fluid_level: Union[Unset, RInstance]
        if isinstance(_washer_fluid_level, Unset):
            washer_fluid_level = UNSET
        else:
            washer_fluid_level = RInstance.from_dict(_washer_fluid_level)

        diagnostic_vals = cls(
            engine_hours_to_service=engine_hours_to_service,
            km_to_service=km_to_service,
            main_battery_status=main_battery_status,
            months_to_service=months_to_service,
            service_type=service_type,
            service_status=service_status,
            service_trigger=service_trigger,
            backup_battery_remaining=backup_battery_remaining,
            washer_fluid_level=washer_fluid_level,
        )

        diagnostic_vals.additional_properties = d
        return diagnostic_vals

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
