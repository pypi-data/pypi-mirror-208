from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelsListResponse200ModelsItem")


@attr.s(auto_attribs=True)
class ModelsListResponse200ModelsItem:
    """  Workspace model details.

        Attributes:
            id (int):  Model identifer.
            name (str):  The descriptive name of the model, the same as `model_id`.
            owner_id (str):  The UUID of the User.
            created_at (Union[Unset, None, str]):  The timestamp that this model was created.
            updated_at (Union[Unset, None, str]):  The last time this model object was updated.
     """

    id: int
    name: str
    owner_id: str
    created_at: Union[Unset, None, str] = UNSET
    updated_at: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        owner_id = self.owner_id
        created_at = self.created_at
        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "owner_id": owner_id,
        })
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        owner_id = d.pop("owner_id")

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        models_list_response_200_models_item = cls(
            id=id,
            name=name,
            owner_id=owner_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        models_list_response_200_models_item.additional_properties = d
        return models_list_response_200_models_item

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
