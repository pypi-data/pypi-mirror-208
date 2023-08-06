from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlateauGetPipelineTopicNameJsonBody")


@attr.s(auto_attribs=True)
class PlateauGetPipelineTopicNameJsonBody:
    """  Request for pipeline topic name.

        Attributes:
            pipeline_name (str):  Pipeline name.
            workspace_id (Union[Unset, None, int]):  Optional workspace identifier.
     """

    pipeline_name: str
    workspace_id: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_name = self.pipeline_name
        workspace_id = self.workspace_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_name": pipeline_name,
        })
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline_name = d.pop("pipeline_name")

        workspace_id = d.pop("workspace_id", UNSET)

        plateau_get_pipeline_topic_name_json_body = cls(
            pipeline_name=pipeline_name,
            workspace_id=workspace_id,
        )

        plateau_get_pipeline_topic_name_json_body.additional_properties = d
        return plateau_get_pipeline_topic_name_json_body

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
