from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ExplainabilityGetConfigJsonBody")


@attr.s(auto_attribs=True)
class ExplainabilityGetConfigJsonBody:
    """ 
        Attributes:
            explainability_config_id (str):  The id of the explainability config to retrieve.
     """

    explainability_config_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        explainability_config_id = self.explainability_config_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "explainability_config_id": explainability_config_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        explainability_config_id = d.pop("explainability_config_id")

        explainability_get_config_json_body = cls(
            explainability_config_id=explainability_config_id,
        )

        explainability_get_config_json_body.additional_properties = d
        return explainability_get_config_json_body

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
