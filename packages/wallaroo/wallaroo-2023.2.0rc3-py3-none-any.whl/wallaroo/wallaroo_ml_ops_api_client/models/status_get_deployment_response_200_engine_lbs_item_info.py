from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.status_get_deployment_response_200_engine_lbs_item_info_health import \
    StatusGetDeploymentResponse200EngineLbsItemInfoHealth
from ..models.status_get_deployment_response_200_engine_lbs_item_info_status import \
    StatusGetDeploymentResponse200EngineLbsItemInfoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.status_get_deployment_response_200_engine_lbs_item_info_labels import \
      StatusGetDeploymentResponse200EngineLbsItemInfoLabels





T = TypeVar("T", bound="StatusGetDeploymentResponse200EngineLbsItemInfo")


@attr.s(auto_attribs=True)
class StatusGetDeploymentResponse200EngineLbsItemInfo:
    """ 
        Attributes:
            name (str):  Pod name.
            status (StatusGetDeploymentResponse200EngineLbsItemInfoStatus):  Pod status.
            details (List[str]):  Details from kubernetes about the pod state.
            labels (StatusGetDeploymentResponse200EngineLbsItemInfoLabels):  Kubernetes labels for the pod
            health (StatusGetDeploymentResponse200EngineLbsItemInfoHealth):  The health of the pod.
            ip (Union[Unset, None, str]):  Pod IP address, if known.
            reason (Union[Unset, None, str]):  Reason for the current pod status, if available.
            required_cpu (Union[Unset, None, str]):  Minimum CPU required by the engine, if known.
            required_memory (Union[Unset, None, str]):  Memory required by the engine, if known.
     """

    name: str
    status: StatusGetDeploymentResponse200EngineLbsItemInfoStatus
    details: List[str]
    labels: 'StatusGetDeploymentResponse200EngineLbsItemInfoLabels'
    health: StatusGetDeploymentResponse200EngineLbsItemInfoHealth
    ip: Union[Unset, None, str] = UNSET
    reason: Union[Unset, None, str] = UNSET
    required_cpu: Union[Unset, None, str] = UNSET
    required_memory: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        status = self.status.value

        details = self.details




        labels = self.labels.to_dict()

        health = self.health.value

        ip = self.ip
        reason = self.reason
        required_cpu = self.required_cpu
        required_memory = self.required_memory

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "status": status,
            "details": details,
            "labels": labels,
            "health": health,
        })
        if ip is not UNSET:
            field_dict["ip"] = ip
        if reason is not UNSET:
            field_dict["reason"] = reason
        if required_cpu is not UNSET:
            field_dict["required_cpu"] = required_cpu
        if required_memory is not UNSET:
            field_dict["required_memory"] = required_memory

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.status_get_deployment_response_200_engine_lbs_item_info_labels import \
            StatusGetDeploymentResponse200EngineLbsItemInfoLabels
        d = src_dict.copy()
        name = d.pop("name")

        status = StatusGetDeploymentResponse200EngineLbsItemInfoStatus(d.pop("status"))




        details = cast(List[str], d.pop("details"))


        labels = StatusGetDeploymentResponse200EngineLbsItemInfoLabels.from_dict(d.pop("labels"))




        health = StatusGetDeploymentResponse200EngineLbsItemInfoHealth(d.pop("health"))




        ip = d.pop("ip", UNSET)

        reason = d.pop("reason", UNSET)

        required_cpu = d.pop("required_cpu", UNSET)

        required_memory = d.pop("required_memory", UNSET)

        status_get_deployment_response_200_engine_lbs_item_info = cls(
            name=name,
            status=status,
            details=details,
            labels=labels,
            health=health,
            ip=ip,
            reason=reason,
            required_cpu=required_cpu,
            required_memory=required_memory,
        )

        status_get_deployment_response_200_engine_lbs_item_info.additional_properties = d
        return status_get_deployment_response_200_engine_lbs_item_info

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
