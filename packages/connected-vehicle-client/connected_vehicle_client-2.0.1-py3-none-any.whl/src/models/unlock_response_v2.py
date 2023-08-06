from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.unlock_result_detail_v2 import UnlockResultDetailV2


T = TypeVar("T", bound="UnlockResponseV2")


@attr.s(auto_attribs=True)
class UnlockResponseV2:
    """
    Attributes:
        status (Union[Unset, int]):
        operation_id (Union[Unset, str]):
        data (Union[Unset, UnlockResultDetailV2]):
    """

    status: Union[Unset, int] = UNSET
    operation_id: Union[Unset, str] = UNSET
    data: Union[Unset, "UnlockResultDetailV2"] = UNSET
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
        from ..models.unlock_result_detail_v2 import UnlockResultDetailV2

        d = src_dict.copy()
        status = d.pop("status", UNSET)

        operation_id = d.pop("operationId", UNSET)

        _data = d.pop("data", UNSET)
        data: Union[Unset, UnlockResultDetailV2]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = UnlockResultDetailV2.from_dict(_data)

        unlock_response_v2 = cls(
            status=status,
            operation_id=operation_id,
            data=data,
        )

        unlock_response_v2.additional_properties = d
        return unlock_response_v2

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
