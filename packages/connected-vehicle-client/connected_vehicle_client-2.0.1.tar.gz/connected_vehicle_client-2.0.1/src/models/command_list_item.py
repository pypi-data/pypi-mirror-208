from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.command_list_item_command import CommandListItemCommand
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommandListItem")


@attr.s(auto_attribs=True)
class CommandListItem:
    """
    Attributes:
        command (Union[Unset, CommandListItemCommand]):
        href (Union[Unset, str]):
    """

    command: Union[Unset, CommandListItemCommand] = UNSET
    href: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        command: Union[Unset, str] = UNSET
        if not isinstance(self.command, Unset):
            command = self.command.value

        href = self.href

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if command is not UNSET:
            field_dict["command"] = command
        if href is not UNSET:
            field_dict["href"] = href

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _command = d.pop("command", UNSET)
        command: Union[Unset, CommandListItemCommand]
        if isinstance(_command, Unset):
            command = UNSET
        else:
            command = CommandListItemCommand(_command)

        href = d.pop("href", UNSET)

        command_list_item = cls(
            command=command,
            href=href,
        )

        command_list_item.additional_properties = d
        return command_list_item

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
