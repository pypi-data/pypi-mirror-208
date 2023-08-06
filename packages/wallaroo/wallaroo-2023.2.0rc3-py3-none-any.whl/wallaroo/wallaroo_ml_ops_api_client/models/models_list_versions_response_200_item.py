from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelsListVersionsResponse200Item")


@attr.s(auto_attribs=True)
class ModelsListVersionsResponse200Item:
    """  Individual model details.

        Attributes:
            sha (str):  Model's content hash.
            models_pk_id (int):  Internal model identifer.
            model_version (str):  Model version.
            owner_id (str):  Model owner identifier.
            model_id (str):  Model identifier.
            id (int):  Internal identifier.
            file_name (Union[Unset, None, str]):  Model filename.
            image_path (Union[Unset, None, str]):  Model image path.
            status (Union[Unset, None, str]):  Model status
     """

    sha: str
    models_pk_id: int
    model_version: str
    owner_id: str
    model_id: str
    id: int
    file_name: Union[Unset, None, str] = UNSET
    image_path: Union[Unset, None, str] = UNSET
    status: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        sha = self.sha
        models_pk_id = self.models_pk_id
        model_version = self.model_version
        owner_id = self.owner_id
        model_id = self.model_id
        id = self.id
        file_name = self.file_name
        image_path = self.image_path
        status = self.status

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "sha": sha,
            "models_pk_id": models_pk_id,
            "model_version": model_version,
            "owner_id": owner_id,
            "model_id": model_id,
            "id": id,
        })
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if image_path is not UNSET:
            field_dict["image_path"] = image_path
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sha = d.pop("sha")

        models_pk_id = d.pop("models_pk_id")

        model_version = d.pop("model_version")

        owner_id = d.pop("owner_id")

        model_id = d.pop("model_id")

        id = d.pop("id")

        file_name = d.pop("file_name", UNSET)

        image_path = d.pop("image_path", UNSET)

        status = d.pop("status", UNSET)

        models_list_versions_response_200_item = cls(
            sha=sha,
            models_pk_id=models_pk_id,
            model_version=model_version,
            owner_id=owner_id,
            model_id=model_id,
            id=id,
            file_name=file_name,
            image_path=image_path,
            status=status,
        )

        models_list_versions_response_200_item.additional_properties = d
        return models_list_versions_response_200_item

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
