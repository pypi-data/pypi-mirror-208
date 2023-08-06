from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelsListVersionsJsonBody")


@attr.s(auto_attribs=True)
class ModelsListVersionsJsonBody:
    """  Request for getting model versions

        Attributes:
            model_id (Union[Unset, None, str]):  Descriptive identifier for the model
            models_pk_id (Union[Unset, None, int]):  Internal numeric identifier for the model
     """

    model_id: Union[Unset, None, str] = UNSET
    models_pk_id: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        model_id = self.model_id
        models_pk_id = self.models_pk_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if model_id is not UNSET:
            field_dict["model_id"] = model_id
        if models_pk_id is not UNSET:
            field_dict["models_pk_id"] = models_pk_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        model_id = d.pop("model_id", UNSET)

        models_pk_id = d.pop("models_pk_id", UNSET)

        models_list_versions_json_body = cls(
            model_id=model_id,
            models_pk_id=models_pk_id,
        )

        models_list_versions_json_body.additional_properties = d
        return models_list_versions_json_body

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
