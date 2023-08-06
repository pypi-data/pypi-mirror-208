from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.status_get_deployment_response_200_engines_item_info import \
      StatusGetDeploymentResponse200EnginesItemInfo
  from ..models.status_get_deployment_response_200_engines_item_model_statuses import \
      StatusGetDeploymentResponse200EnginesItemModelStatuses
  from ..models.status_get_deployment_response_200_engines_item_pipeline_statuses import \
      StatusGetDeploymentResponse200EnginesItemPipelineStatuses





T = TypeVar("T", bound="StatusGetDeploymentResponse200EnginesItem")


@attr.s(auto_attribs=True)
class StatusGetDeploymentResponse200EnginesItem:
    """  Engine deployment status.

        Attributes:
            info (StatusGetDeploymentResponse200EnginesItemInfo):
            pipeline_statuses (Union[Unset, None, StatusGetDeploymentResponse200EnginesItemPipelineStatuses]):  Statuses of
                pipelines serviced by the engine.
            model_statuses (Union[Unset, None, StatusGetDeploymentResponse200EnginesItemModelStatuses]):  Statuses of models
                executed by the engine.
     """

    info: 'StatusGetDeploymentResponse200EnginesItemInfo'
    pipeline_statuses: Union[Unset, None, 'StatusGetDeploymentResponse200EnginesItemPipelineStatuses'] = UNSET
    model_statuses: Union[Unset, None, 'StatusGetDeploymentResponse200EnginesItemModelStatuses'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        info = self.info.to_dict()

        pipeline_statuses: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.pipeline_statuses, Unset):
            pipeline_statuses = self.pipeline_statuses.to_dict() if self.pipeline_statuses else None

        model_statuses: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.model_statuses, Unset):
            model_statuses = self.model_statuses.to_dict() if self.model_statuses else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "info": info,
        })
        if pipeline_statuses is not UNSET:
            field_dict["pipeline_statuses"] = pipeline_statuses
        if model_statuses is not UNSET:
            field_dict["model_statuses"] = model_statuses

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.status_get_deployment_response_200_engines_item_info import \
            StatusGetDeploymentResponse200EnginesItemInfo
        from ..models.status_get_deployment_response_200_engines_item_model_statuses import \
            StatusGetDeploymentResponse200EnginesItemModelStatuses
        from ..models.status_get_deployment_response_200_engines_item_pipeline_statuses import \
            StatusGetDeploymentResponse200EnginesItemPipelineStatuses
        d = src_dict.copy()
        info = StatusGetDeploymentResponse200EnginesItemInfo.from_dict(d.pop("info"))




        _pipeline_statuses = d.pop("pipeline_statuses", UNSET)
        pipeline_statuses: Union[Unset, None, StatusGetDeploymentResponse200EnginesItemPipelineStatuses]
        if _pipeline_statuses is None:
            pipeline_statuses = None
        elif isinstance(_pipeline_statuses,  Unset):
            pipeline_statuses = UNSET
        else:
            pipeline_statuses = StatusGetDeploymentResponse200EnginesItemPipelineStatuses.from_dict(_pipeline_statuses)




        _model_statuses = d.pop("model_statuses", UNSET)
        model_statuses: Union[Unset, None, StatusGetDeploymentResponse200EnginesItemModelStatuses]
        if _model_statuses is None:
            model_statuses = None
        elif isinstance(_model_statuses,  Unset):
            model_statuses = UNSET
        else:
            model_statuses = StatusGetDeploymentResponse200EnginesItemModelStatuses.from_dict(_model_statuses)




        status_get_deployment_response_200_engines_item = cls(
            info=info,
            pipeline_statuses=pipeline_statuses,
            model_statuses=model_statuses,
        )

        status_get_deployment_response_200_engines_item.additional_properties = d
        return status_get_deployment_response_200_engines_item

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
