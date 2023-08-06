from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspacesListUsersResponse200UsersItem")


@attr.s(auto_attribs=True)
class WorkspacesListUsersResponse200UsersItem:
    """  User data returned as part of the List Workspace Users call

        Attributes:
            user_id (str):  User UUID identifier
            user_type (Union[Unset, None, str]):  User type, Collaborator or Owner
     """

    user_id: str
    user_type: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id
        user_type = self.user_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "user_id": user_id,
        })
        if user_type is not UNSET:
            field_dict["user_type"] = user_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id")

        user_type = d.pop("user_type", UNSET)

        workspaces_list_users_response_200_users_item = cls(
            user_id=user_id,
            user_type=user_type,
        )

        workspaces_list_users_response_200_users_item.additional_properties = d
        return workspaces_list_users_response_200_users_item

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
