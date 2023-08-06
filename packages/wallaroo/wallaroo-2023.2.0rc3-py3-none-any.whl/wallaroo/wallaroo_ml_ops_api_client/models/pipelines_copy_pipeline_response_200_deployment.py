from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PipelinesCopyPipelineResponse200Deployment")


@attr.s(auto_attribs=True)
class PipelinesCopyPipelineResponse200Deployment:
    """  Pipeline deployment response.

        Attributes:
            id (int):
     """

    id: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        pipelines_copy_pipeline_response_200_deployment = cls(
            id=id,
        )

        pipelines_copy_pipeline_response_200_deployment.additional_properties = d
        return pipelines_copy_pipeline_response_200_deployment

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
