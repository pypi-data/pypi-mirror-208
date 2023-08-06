from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.models_upload_response_200_insert_models import \
      ModelsUploadResponse200InsertModels





T = TypeVar("T", bound="ModelsUploadResponse200")


@attr.s(auto_attribs=True)
class ModelsUploadResponse200:
    """  Successful response to model upload.

        Attributes:
            insert_models (Union[Unset, None, ModelsUploadResponse200InsertModels]):  Response payload wrapper.
     """

    insert_models: Union[Unset, None, 'ModelsUploadResponse200InsertModels'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        insert_models: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.insert_models, Unset):
            insert_models = self.insert_models.to_dict() if self.insert_models else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if insert_models is not UNSET:
            field_dict["insert_models"] = insert_models

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.models_upload_response_200_insert_models import \
            ModelsUploadResponse200InsertModels
        d = src_dict.copy()
        _insert_models = d.pop("insert_models", UNSET)
        insert_models: Union[Unset, None, ModelsUploadResponse200InsertModels]
        if _insert_models is None:
            insert_models = None
        elif isinstance(_insert_models,  Unset):
            insert_models = UNSET
        else:
            insert_models = ModelsUploadResponse200InsertModels.from_dict(_insert_models)




        models_upload_response_200 = cls(
            insert_models=insert_models,
        )

        models_upload_response_200.additional_properties = d
        return models_upload_response_200

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
