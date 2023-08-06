from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlateauGetTopicNameJsonBody")


@attr.s(auto_attribs=True)
class PlateauGetTopicNameJsonBody:
    """  Request for topic name.

        Attributes:
            workspace_id (Union[Unset, None, int]):  Workspace identifier.
            pipeline_name (Union[Unset, None, str]):  Pipeline name.
            pipeline_pk_id (Union[Unset, None, int]):  Internal pipeline identifier.
     """

    workspace_id: Union[Unset, None, int] = UNSET
    pipeline_name: Union[Unset, None, str] = UNSET
    pipeline_pk_id: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        pipeline_name = self.pipeline_name
        pipeline_pk_id = self.pipeline_pk_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if pipeline_name is not UNSET:
            field_dict["pipeline_name"] = pipeline_name
        if pipeline_pk_id is not UNSET:
            field_dict["pipeline_pk_id"] = pipeline_pk_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id", UNSET)

        pipeline_name = d.pop("pipeline_name", UNSET)

        pipeline_pk_id = d.pop("pipeline_pk_id", UNSET)

        plateau_get_topic_name_json_body = cls(
            workspace_id=workspace_id,
            pipeline_name=pipeline_name,
            pipeline_pk_id=pipeline_pk_id,
        )

        plateau_get_topic_name_json_body.additional_properties = d
        return plateau_get_topic_name_json_body

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
