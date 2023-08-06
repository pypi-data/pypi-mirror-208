from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance


T = TypeVar("T", bound="DoorAndLockStatus")


@attr.s(auto_attribs=True)
class DoorAndLockStatus:
    """
    Attributes:
        car_locked (Union[Unset, RInstance]):
        rear_right (Union[Unset, RInstance]):
        front_right (Union[Unset, RInstance]):
        front_left (Union[Unset, RInstance]):
        rear_left (Union[Unset, RInstance]):
        cap (Union[Unset, RInstance]):
        hood (Union[Unset, RInstance]):
        tail_gate (Union[Unset, RInstance]):
    """

    car_locked: Union[Unset, "RInstance"] = UNSET
    rear_right: Union[Unset, "RInstance"] = UNSET
    front_right: Union[Unset, "RInstance"] = UNSET
    front_left: Union[Unset, "RInstance"] = UNSET
    rear_left: Union[Unset, "RInstance"] = UNSET
    cap: Union[Unset, "RInstance"] = UNSET
    hood: Union[Unset, "RInstance"] = UNSET
    tail_gate: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        car_locked: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.car_locked, Unset):
            car_locked = self.car_locked.to_dict()

        rear_right: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rear_right, Unset):
            rear_right = self.rear_right.to_dict()

        front_right: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.front_right, Unset):
            front_right = self.front_right.to_dict()

        front_left: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.front_left, Unset):
            front_left = self.front_left.to_dict()

        rear_left: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rear_left, Unset):
            rear_left = self.rear_left.to_dict()

        cap: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cap, Unset):
            cap = self.cap.to_dict()

        hood: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.hood, Unset):
            hood = self.hood.to_dict()

        tail_gate: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.tail_gate, Unset):
            tail_gate = self.tail_gate.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if car_locked is not UNSET:
            field_dict["carLocked"] = car_locked
        if rear_right is not UNSET:
            field_dict["rearRight"] = rear_right
        if front_right is not UNSET:
            field_dict["frontRight"] = front_right
        if front_left is not UNSET:
            field_dict["frontLeft"] = front_left
        if rear_left is not UNSET:
            field_dict["rearLeft"] = rear_left
        if cap is not UNSET:
            field_dict["cap"] = cap
        if hood is not UNSET:
            field_dict["hood"] = hood
        if tail_gate is not UNSET:
            field_dict["tailGate"] = tail_gate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance

        d = src_dict.copy()
        _car_locked = d.pop("carLocked", UNSET)
        car_locked: Union[Unset, RInstance]
        if isinstance(_car_locked, Unset):
            car_locked = UNSET
        else:
            car_locked = RInstance.from_dict(_car_locked)

        _rear_right = d.pop("rearRight", UNSET)
        rear_right: Union[Unset, RInstance]
        if isinstance(_rear_right, Unset):
            rear_right = UNSET
        else:
            rear_right = RInstance.from_dict(_rear_right)

        _front_right = d.pop("frontRight", UNSET)
        front_right: Union[Unset, RInstance]
        if isinstance(_front_right, Unset):
            front_right = UNSET
        else:
            front_right = RInstance.from_dict(_front_right)

        _front_left = d.pop("frontLeft", UNSET)
        front_left: Union[Unset, RInstance]
        if isinstance(_front_left, Unset):
            front_left = UNSET
        else:
            front_left = RInstance.from_dict(_front_left)

        _rear_left = d.pop("rearLeft", UNSET)
        rear_left: Union[Unset, RInstance]
        if isinstance(_rear_left, Unset):
            rear_left = UNSET
        else:
            rear_left = RInstance.from_dict(_rear_left)

        _cap = d.pop("cap", UNSET)
        cap: Union[Unset, RInstance]
        if isinstance(_cap, Unset):
            cap = UNSET
        else:
            cap = RInstance.from_dict(_cap)

        _hood = d.pop("hood", UNSET)
        hood: Union[Unset, RInstance]
        if isinstance(_hood, Unset):
            hood = UNSET
        else:
            hood = RInstance.from_dict(_hood)

        _tail_gate = d.pop("tailGate", UNSET)
        tail_gate: Union[Unset, RInstance]
        if isinstance(_tail_gate, Unset):
            tail_gate = UNSET
        else:
            tail_gate = RInstance.from_dict(_tail_gate)

        door_and_lock_status = cls(
            car_locked=car_locked,
            rear_right=rear_right,
            front_right=front_right,
            front_left=front_left,
            rear_left=rear_left,
            cap=cap,
            hood=hood,
            tail_gate=tail_gate,
        )

        door_and_lock_status.additional_properties = d
        return door_and_lock_status

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
