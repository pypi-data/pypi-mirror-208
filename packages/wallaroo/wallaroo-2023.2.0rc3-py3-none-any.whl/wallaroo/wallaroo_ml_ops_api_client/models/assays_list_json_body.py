from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssaysListJsonBody")


@attr.s(auto_attribs=True)
class AssaysListJsonBody:
    """  Request for list of assays.

        Attributes:
            pipeline_id (Union[Unset, None, int]):  Optional pipeline identifier.
     """

    pipeline_id: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_id = self.pipeline_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if pipeline_id is not UNSET:
            field_dict["pipeline_id"] = pipeline_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline_id = d.pop("pipeline_id", UNSET)

        assays_list_json_body = cls(
            pipeline_id=pipeline_id,
        )

        assays_list_json_body.additional_properties = d
        return assays_list_json_body

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
