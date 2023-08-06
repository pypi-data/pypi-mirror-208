from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.pipelines_copy_pipeline_response_200_deployment import \
      PipelinesCopyPipelineResponse200Deployment





T = TypeVar("T", bound="PipelinesCopyPipelineResponse200")


@attr.s(auto_attribs=True)
class PipelinesCopyPipelineResponse200:
    """  Successful response to pipeline copy request.

        Attributes:
            pipeline_pk_id (int):  Internal pipeline identifier.
            pipeline_variant_pk_id (int):  Internal pipeline variant identifier.
            pipeline_version (Union[Unset, None, str]):  Pipeline version created.
            deployment (Union[Unset, None, PipelinesCopyPipelineResponse200Deployment]):  Pipeline deployment response.
     """

    pipeline_pk_id: int
    pipeline_variant_pk_id: int
    pipeline_version: Union[Unset, None, str] = UNSET
    deployment: Union[Unset, None, 'PipelinesCopyPipelineResponse200Deployment'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_pk_id = self.pipeline_pk_id
        pipeline_variant_pk_id = self.pipeline_variant_pk_id
        pipeline_version = self.pipeline_version
        deployment: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.deployment, Unset):
            deployment = self.deployment.to_dict() if self.deployment else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_pk_id": pipeline_pk_id,
            "pipeline_variant_pk_id": pipeline_variant_pk_id,
        })
        if pipeline_version is not UNSET:
            field_dict["pipeline_version"] = pipeline_version
        if deployment is not UNSET:
            field_dict["deployment"] = deployment

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pipelines_copy_pipeline_response_200_deployment import \
            PipelinesCopyPipelineResponse200Deployment
        d = src_dict.copy()
        pipeline_pk_id = d.pop("pipeline_pk_id")

        pipeline_variant_pk_id = d.pop("pipeline_variant_pk_id")

        pipeline_version = d.pop("pipeline_version", UNSET)

        _deployment = d.pop("deployment", UNSET)
        deployment: Union[Unset, None, PipelinesCopyPipelineResponse200Deployment]
        if _deployment is None:
            deployment = None
        elif isinstance(_deployment,  Unset):
            deployment = UNSET
        else:
            deployment = PipelinesCopyPipelineResponse200Deployment.from_dict(_deployment)




        pipelines_copy_pipeline_response_200 = cls(
            pipeline_pk_id=pipeline_pk_id,
            pipeline_variant_pk_id=pipeline_variant_pk_id,
            pipeline_version=pipeline_version,
            deployment=deployment,
        )

        pipelines_copy_pipeline_response_200.additional_properties = d
        return pipelines_copy_pipeline_response_200

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
