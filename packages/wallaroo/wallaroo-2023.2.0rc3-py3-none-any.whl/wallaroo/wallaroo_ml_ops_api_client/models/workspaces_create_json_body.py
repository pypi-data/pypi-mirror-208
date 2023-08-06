from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="WorkspacesCreateJsonBody")


@attr.s(auto_attribs=True)
class WorkspacesCreateJsonBody:
    """  Request to create a new Workspace

        Attributes:
            workspace_name (str):  Descriptive name for the new workspace
     """

    workspace_name: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_name = self.workspace_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_name": workspace_name,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_name = d.pop("workspace_name")

        workspaces_create_json_body = cls(
            workspace_name=workspace_name,
        )

        workspaces_create_json_body.additional_properties = d
        return workspaces_create_json_body

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
