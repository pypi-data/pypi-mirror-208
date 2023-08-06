from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspacesRemoveUserJsonBody")


@attr.s(auto_attribs=True)
class WorkspacesRemoveUserJsonBody:
    """  Request to remove a User from a Workspace

        Attributes:
            workspace_id (int):  Workspace to remove the User from.
            email (Union[Unset, None, str]):  Email of the User to remove.
            user_id (Union[Unset, None, str]):  UUID ID of the User to remove.
     """

    workspace_id: int
    email: Union[Unset, None, str] = UNSET
    user_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        email = self.email
        user_id = self.user_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_id": workspace_id,
        })
        if email is not UNSET:
            field_dict["email"] = email
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        email = d.pop("email", UNSET)

        user_id = d.pop("user_id", UNSET)

        workspaces_remove_user_json_body = cls(
            workspace_id=workspace_id,
            email=email,
            user_id=user_id,
        )

        workspaces_remove_user_json_body.additional_properties = d
        return workspaces_remove_user_json_body

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
