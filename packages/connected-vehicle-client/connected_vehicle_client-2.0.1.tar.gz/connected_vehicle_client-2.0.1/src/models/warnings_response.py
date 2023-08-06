from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.warning_vals import WarningVals


T = TypeVar("T", bound="WarningsResponse")


@attr.s(auto_attribs=True)
class WarningsResponse:
    """
    Attributes:
        status (Union[Unset, int]):
        operation_id (Union[Unset, str]):
        data (Union[Unset, WarningVals]):
    """

    status: Union[Unset, int] = UNSET
    operation_id: Union[Unset, str] = UNSET
    data: Union[Unset, "WarningVals"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status
        operation_id = self.operation_id
        data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if operation_id is not UNSET:
            field_dict["operationId"] = operation_id
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.warning_vals import WarningVals

        d = src_dict.copy()
        status = d.pop("status", UNSET)

        operation_id = d.pop("operationId", UNSET)

        _data = d.pop("data", UNSET)
        data: Union[Unset, WarningVals]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = WarningVals.from_dict(_data)

        warnings_response = cls(
            status=status,
            operation_id=operation_id,
            data=data,
        )

        warnings_response.additional_properties = d
        return warnings_response

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
