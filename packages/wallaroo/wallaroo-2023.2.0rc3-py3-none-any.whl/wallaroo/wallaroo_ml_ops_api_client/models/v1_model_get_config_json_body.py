from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="V1ModelGetConfigJsonBody")


@attr.s(auto_attribs=True)
class V1ModelGetConfigJsonBody:
    """  Body for request to /models/get_config_by_id

        Attributes:
            model_id (int):  The primary key of a model
     """

    model_id: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        model_id = self.model_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "model_id": model_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        model_id = d.pop("model_id")

        v1_model_get_config_json_body = cls(
            model_id=model_id,
        )

        v1_model_get_config_json_body.additional_properties = d
        return v1_model_get_config_json_body

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
