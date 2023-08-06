from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
  from ..models.models_list_response_200_models_item import \
      ModelsListResponse200ModelsItem





T = TypeVar("T", bound="ModelsListResponse200")


@attr.s(auto_attribs=True)
class ModelsListResponse200:
    """  Successful response to workspace model retrieval.

        Attributes:
            models (List['ModelsListResponse200ModelsItem']):  List of models in the workspace.
     """

    models: List['ModelsListResponse200ModelsItem']
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        models = []
        for models_item_data in self.models:
            models_item = models_item_data.to_dict()

            models.append(models_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "models": models,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.models_list_response_200_models_item import \
            ModelsListResponse200ModelsItem
        d = src_dict.copy()
        models = []
        _models = d.pop("models")
        for models_item_data in (_models):
            models_item = ModelsListResponse200ModelsItem.from_dict(models_item_data)



            models.append(models_item)


        models_list_response_200 = cls(
            models=models,
        )

        models_list_response_200.additional_properties = d
        return models_list_response_200

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
