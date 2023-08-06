from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ExplainabilityGetResultJsonBody")


@attr.s(auto_attribs=True)
class ExplainabilityGetResultJsonBody:
    """ 
        Attributes:
            explainability_result_id (str):  Gets the result for an explainability request.  Note the id of the request and
                result are the same.
     """

    explainability_result_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        explainability_result_id = self.explainability_result_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "explainability_result_id": explainability_result_id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        explainability_result_id = d.pop("explainability_result_id")

        explainability_get_result_json_body = cls(
            explainability_result_id=explainability_result_id,
        )

        explainability_get_result_json_body.additional_properties = d
        return explainability_get_result_json_body

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
