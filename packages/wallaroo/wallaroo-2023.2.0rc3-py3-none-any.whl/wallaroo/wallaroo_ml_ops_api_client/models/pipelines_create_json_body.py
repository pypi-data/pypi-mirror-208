from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.pipelines_create_json_body_definition import \
      PipelinesCreateJsonBodyDefinition





T = TypeVar("T", bound="PipelinesCreateJsonBody")


@attr.s(auto_attribs=True)
class PipelinesCreateJsonBody:
    """  Request to create a new pipeline in a workspace.

        Attributes:
            pipeline_id (str):  Pipeline identifier.
            workspace_id (int):  Workspace identifier.
            definition (Union[Unset, None, PipelinesCreateJsonBodyDefinition]):  Pipeline definition.
     """

    pipeline_id: str
    workspace_id: int
    definition: Union[Unset, None, 'PipelinesCreateJsonBodyDefinition'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_id = self.pipeline_id
        workspace_id = self.workspace_id
        definition: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.definition, Unset):
            definition = self.definition.to_dict() if self.definition else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_id": pipeline_id,
            "workspace_id": workspace_id,
        })
        if definition is not UNSET:
            field_dict["definition"] = definition

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pipelines_create_json_body_definition import \
            PipelinesCreateJsonBodyDefinition
        d = src_dict.copy()
        pipeline_id = d.pop("pipeline_id")

        workspace_id = d.pop("workspace_id")

        _definition = d.pop("definition", UNSET)
        definition: Union[Unset, None, PipelinesCreateJsonBodyDefinition]
        if _definition is None:
            definition = None
        elif isinstance(_definition,  Unset):
            definition = UNSET
        else:
            definition = PipelinesCreateJsonBodyDefinition.from_dict(_definition)




        pipelines_create_json_body = cls(
            pipeline_id=pipeline_id,
            workspace_id=workspace_id,
            definition=definition,
        )

        pipelines_create_json_body.additional_properties = d
        return pipelines_create_json_body

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
