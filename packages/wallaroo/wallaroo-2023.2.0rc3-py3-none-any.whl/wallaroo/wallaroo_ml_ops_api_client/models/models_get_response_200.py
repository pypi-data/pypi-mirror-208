from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.models_get_response_200_models_item import \
      ModelsGetResponse200ModelsItem





T = TypeVar("T", bound="ModelsGetResponse200")


@attr.s(auto_attribs=True)
class ModelsGetResponse200:
    """  Successful response to workspace model retrieval.  Details for a single Models object in the workspace.

        Attributes:
            id (int):  Model identifer.
            name (str):  The descriptive name of the model, the same as `model_id`.
            owner_id (str):  The UUID of the User.
            models (List['ModelsGetResponse200ModelsItem']):
            created_at (Union[Unset, None, str]):  The timestamp that this model was created.
            updated_at (Union[Unset, None, str]):  The last time this model object was updated.
     """

    id: int
    name: str
    owner_id: str
    models: List['ModelsGetResponse200ModelsItem']
    created_at: Union[Unset, None, str] = UNSET
    updated_at: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        owner_id = self.owner_id
        models = []
        for models_item_data in self.models:
            models_item = models_item_data.to_dict()

            models.append(models_item)




        created_at = self.created_at
        updated_at = self.updated_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "owner_id": owner_id,
            "models": models,
        })
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.models_get_response_200_models_item import \
            ModelsGetResponse200ModelsItem
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        owner_id = d.pop("owner_id")

        models = []
        _models = d.pop("models")
        for models_item_data in (_models):
            models_item = ModelsGetResponse200ModelsItem.from_dict(models_item_data)



            models.append(models_item)


        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        models_get_response_200 = cls(
            id=id,
            name=name,
            owner_id=owner_id,
            models=models,
            created_at=created_at,
            updated_at=updated_at,
        )

        models_get_response_200.additional_properties = d
        return models_get_response_200

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
