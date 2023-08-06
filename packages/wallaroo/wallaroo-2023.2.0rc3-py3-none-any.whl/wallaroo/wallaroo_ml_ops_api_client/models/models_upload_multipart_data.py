from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.models_upload_multipart_data_visibility import \
    ModelsUploadMultipartDataVisibility
from ..types import Unset

T = TypeVar("T", bound="ModelsUploadMultipartData")


@attr.s(auto_attribs=True)
class ModelsUploadMultipartData:
    """  Model upload request.

        Attributes:
            name (str):  Model name.
            visibility (ModelsUploadMultipartDataVisibility):  Desired model visibility.
            workspace_id (int):  Workspace identifier.
     """

    name: str
    visibility: ModelsUploadMultipartDataVisibility
    workspace_id: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        visibility = self.visibility.value

        workspace_id = self.workspace_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "visibility": visibility,
            "workspace_id": workspace_id,
        })

        return field_dict


    def to_multipart(self) -> Dict[str, Any]:
        name = self.name if isinstance(self.name, Unset) else (None, str(self.name).encode(), "text/plain")
        visibility = (None, str(self.visibility.value).encode(), "text/plain")

        workspace_id = self.workspace_id if isinstance(self.workspace_id, Unset) else (None, str(self.workspace_id).encode(), "text/plain")

        field_dict: Dict[str, Any] = {}
        field_dict.update({
            key: (None, str(value).encode(), "text/plain")
            for key, value in self.additional_properties.items()
        })
        field_dict.update({
            "name": name,
            "visibility": visibility,
            "workspace_id": workspace_id,
        })

        return field_dict


    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        visibility = ModelsUploadMultipartDataVisibility(d.pop("visibility"))




        workspace_id = d.pop("workspace_id")

        models_upload_multipart_data = cls(
            name=name,
            visibility=visibility,
            workspace_id=workspace_id,
        )

        models_upload_multipart_data.additional_properties = d
        return models_upload_multipart_data

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
