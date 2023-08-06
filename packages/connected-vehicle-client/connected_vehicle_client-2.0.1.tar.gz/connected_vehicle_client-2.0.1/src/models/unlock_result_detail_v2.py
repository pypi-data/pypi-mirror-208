from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.unlock_result_detail_v2_invoke_status import UnlockResultDetailV2InvokeStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="UnlockResultDetailV2")


@attr.s(auto_attribs=True)
class UnlockResultDetailV2:
    """
    Attributes:
        vin (Union[Unset, str]):
        status (Union[Unset, str]):
        status_code (Union[Unset, int]):
        operation_id (Union[Unset, str]):
        invoke_status (Union[Unset, UnlockResultDetailV2InvokeStatus]):
        message (Union[Unset, str]):
        ready_to_unlock (Union[Unset, bool]):
        ready_to_unlock_until (Union[Unset, int]):
    """

    vin: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    status_code: Union[Unset, int] = UNSET
    operation_id: Union[Unset, str] = UNSET
    invoke_status: Union[Unset, UnlockResultDetailV2InvokeStatus] = UNSET
    message: Union[Unset, str] = UNSET
    ready_to_unlock: Union[Unset, bool] = UNSET
    ready_to_unlock_until: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        vin = self.vin
        status = self.status
        status_code = self.status_code
        operation_id = self.operation_id
        invoke_status: Union[Unset, str] = UNSET
        if not isinstance(self.invoke_status, Unset):
            invoke_status = self.invoke_status.value

        message = self.message
        ready_to_unlock = self.ready_to_unlock
        ready_to_unlock_until = self.ready_to_unlock_until

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vin is not UNSET:
            field_dict["vin"] = vin
        if status is not UNSET:
            field_dict["status"] = status
        if status_code is not UNSET:
            field_dict["statusCode"] = status_code
        if operation_id is not UNSET:
            field_dict["operationId"] = operation_id
        if invoke_status is not UNSET:
            field_dict["invokeStatus"] = invoke_status
        if message is not UNSET:
            field_dict["message"] = message
        if ready_to_unlock is not UNSET:
            field_dict["readyToUnlock"] = ready_to_unlock
        if ready_to_unlock_until is not UNSET:
            field_dict["readyToUnlockUntil"] = ready_to_unlock_until

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        vin = d.pop("vin", UNSET)

        status = d.pop("status", UNSET)

        status_code = d.pop("statusCode", UNSET)

        operation_id = d.pop("operationId", UNSET)

        _invoke_status = d.pop("invokeStatus", UNSET)
        invoke_status: Union[Unset, UnlockResultDetailV2InvokeStatus]
        if isinstance(_invoke_status, Unset):
            invoke_status = UNSET
        else:
            invoke_status = UnlockResultDetailV2InvokeStatus(_invoke_status)

        message = d.pop("message", UNSET)

        ready_to_unlock = d.pop("readyToUnlock", UNSET)

        ready_to_unlock_until = d.pop("readyToUnlockUntil", UNSET)

        unlock_result_detail_v2 = cls(
            vin=vin,
            status=status,
            status_code=status_code,
            operation_id=operation_id,
            invoke_status=invoke_status,
            message=message,
            ready_to_unlock=ready_to_unlock,
            ready_to_unlock_until=ready_to_unlock_until,
        )

        unlock_result_detail_v2.additional_properties = d
        return unlock_result_detail_v2

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
