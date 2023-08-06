from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error import Error


T = TypeVar("T", bound="ErrorResponse")


@attr.s(auto_attribs=True)
class ErrorResponse:
    """
    Attributes:
        status (Union[Unset, int]):
        operation_id (Union[Unset, str]):
        error (Union[Unset, Error]):
    """

    status: Union[Unset, int] = UNSET
    operation_id: Union[Unset, str] = UNSET
    error: Union[Unset, "Error"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status
        operation_id = self.operation_id
        error: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if operation_id is not UNSET:
            field_dict["operationId"] = operation_id
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.error import Error

        d = src_dict.copy()
        status = d.pop("status", UNSET)

        operation_id = d.pop("operationId", UNSET)

        _error = d.pop("error", UNSET)
        error: Union[Unset, Error]
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = Error.from_dict(_error)

        error_response = cls(
            status=status,
            operation_id=operation_id,
            error=error,
        )

        error_response.additional_properties = d
        return error_response

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
