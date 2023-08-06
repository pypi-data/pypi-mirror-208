from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.r_instance import RInstance


T = TypeVar("T", bound="EngineStatus")


@attr.s(auto_attribs=True)
class EngineStatus:
    """
    Attributes:
        engine_running (Union[Unset, RInstance]):
    """

    engine_running: Union[Unset, "RInstance"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        engine_running: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_running, Unset):
            engine_running = self.engine_running.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if engine_running is not UNSET:
            field_dict["engineRunning"] = engine_running

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.r_instance import RInstance

        d = src_dict.copy()
        _engine_running = d.pop("engineRunning", UNSET)
        engine_running: Union[Unset, RInstance]
        if isinstance(_engine_running, Unset):
            engine_running = UNSET
        else:
            engine_running = RInstance.from_dict(_engine_running)

        engine_status = cls(
            engine_running=engine_running,
        )

        engine_status.additional_properties = d
        return engine_status

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
