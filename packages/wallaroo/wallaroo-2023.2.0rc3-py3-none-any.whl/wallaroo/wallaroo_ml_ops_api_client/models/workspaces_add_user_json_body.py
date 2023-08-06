from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspacesAddUserJsonBody")


@attr.s(auto_attribs=True)
class WorkspacesAddUserJsonBody:
    """  Request for adding a user to workspace.

        Attributes:
            workspace_id (int):  Workspace identifier.
            email (Union[Unset, None, str]):  User's email address.
            user_id (Union[Unset, None, str]):  User identifier.
            url (Union[Unset, None, str]):  Workspace URL.
            user_type (Union[Unset, None, str]):  User's role in the workspace. Defaults to Collaborator.
     """

    workspace_id: int
    email: Union[Unset, None, str] = UNSET
    user_id: Union[Unset, None, str] = UNSET
    url: Union[Unset, None, str] = UNSET
    user_type: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        email = self.email
        user_id = self.user_id
        url = self.url
        user_type = self.user_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_id": workspace_id,
        })
        if email is not UNSET:
            field_dict["email"] = email
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if url is not UNSET:
            field_dict["url"] = url
        if user_type is not UNSET:
            field_dict["user_type"] = user_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        email = d.pop("email", UNSET)

        user_id = d.pop("user_id", UNSET)

        url = d.pop("url", UNSET)

        user_type = d.pop("user_type", UNSET)

        workspaces_add_user_json_body = cls(
            workspace_id=workspace_id,
            email=email,
            user_id=user_id,
            url=url,
            user_type=user_type,
        )

        workspaces_add_user_json_body.additional_properties = d
        return workspaces_add_user_json_body

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
