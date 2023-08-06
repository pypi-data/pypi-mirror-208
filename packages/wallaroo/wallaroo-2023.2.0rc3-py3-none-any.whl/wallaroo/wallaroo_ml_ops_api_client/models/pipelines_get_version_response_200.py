from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.pipelines_get_version_response_200_definition import \
      PipelinesGetVersionResponse200Definition





T = TypeVar("T", bound="PipelinesGetVersionResponse200")


@attr.s(auto_attribs=True)
class PipelinesGetVersionResponse200:
    """ 
        Attributes:
            pipeline_id (str):
            version (str):
            definition (Union[Unset, None, PipelinesGetVersionResponse200Definition]):
     """

    pipeline_id: str
    version: str
    definition: Union[Unset, None, 'PipelinesGetVersionResponse200Definition'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_id = self.pipeline_id
        version = self.version
        definition: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.definition, Unset):
            definition = self.definition.to_dict() if self.definition else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_id": pipeline_id,
            "version": version,
        })
        if definition is not UNSET:
            field_dict["definition"] = definition

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pipelines_get_version_response_200_definition import \
            PipelinesGetVersionResponse200Definition
        d = src_dict.copy()
        pipeline_id = d.pop("pipeline_id")

        version = d.pop("version")

        _definition = d.pop("definition", UNSET)
        definition: Union[Unset, None, PipelinesGetVersionResponse200Definition]
        if _definition is None:
            definition = None
        elif isinstance(_definition,  Unset):
            definition = UNSET
        else:
            definition = PipelinesGetVersionResponse200Definition.from_dict(_definition)




        pipelines_get_version_response_200 = cls(
            pipeline_id=pipeline_id,
            version=version,
            definition=definition,
        )

        pipelines_get_version_response_200.additional_properties = d
        return pipelines_get_version_response_200

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
