from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="AssaysRunInteractiveJsonBodyBaselineType0UserProvided")


@attr.s(auto_attribs=True)
class AssaysRunInteractiveJsonBodyBaselineType0UserProvided:
    """ 
        Attributes:
            url (str):
     """

    url: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "url": url,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        url = d.pop("url")

        assays_run_interactive_json_body_baseline_type_0_user_provided = cls(
            url=url,
        )

        assays_run_interactive_json_body_baseline_type_0_user_provided.additional_properties = d
        return assays_run_interactive_json_body_baseline_type_0_user_provided

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
