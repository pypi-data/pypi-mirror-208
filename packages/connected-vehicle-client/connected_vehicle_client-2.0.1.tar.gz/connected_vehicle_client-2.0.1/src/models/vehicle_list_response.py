from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pagination import Pagination
    from ..models.vehicle_list_item import VehicleListItem


T = TypeVar("T", bound="VehicleListResponse")


@attr.s(auto_attribs=True)
class VehicleListResponse:
    """
    Attributes:
        status (Union[Unset, int]):
        operation_id (Union[Unset, str]):
        data (Union[Unset, List['VehicleListItem']]):
        pagination (Union[Unset, Pagination]):
    """

    status: Union[Unset, int] = UNSET
    operation_id: Union[Unset, str] = UNSET
    data: Union[Unset, List["VehicleListItem"]] = UNSET
    pagination: Union[Unset, "Pagination"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status
        operation_id = self.operation_id
        data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()

                data.append(data_item)

        pagination: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if operation_id is not UNSET:
            field_dict["operationId"] = operation_id
        if data is not UNSET:
            field_dict["data"] = data
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pagination import Pagination
        from ..models.vehicle_list_item import VehicleListItem

        d = src_dict.copy()
        status = d.pop("status", UNSET)

        operation_id = d.pop("operationId", UNSET)

        data = []
        _data = d.pop("data", UNSET)
        for data_item_data in _data or []:
            data_item = VehicleListItem.from_dict(data_item_data)

            data.append(data_item)

        _pagination = d.pop("pagination", UNSET)
        pagination: Union[Unset, Pagination]
        if isinstance(_pagination, Unset):
            pagination = UNSET
        else:
            pagination = Pagination.from_dict(_pagination)

        vehicle_list_response = cls(
            status=status,
            operation_id=operation_id,
            data=data,
            pagination=pagination,
        )

        vehicle_list_response.additional_properties = d
        return vehicle_list_response

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
