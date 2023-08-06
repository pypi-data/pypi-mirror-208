from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.status_get_deployment_response_200_sidekicks_item_info import \
      StatusGetDeploymentResponse200SidekicksItemInfo





T = TypeVar("T", bound="StatusGetDeploymentResponse200SidekicksItem")


@attr.s(auto_attribs=True)
class StatusGetDeploymentResponse200SidekicksItem:
    """  Sidekick engine deployment status.

        Attributes:
            info (StatusGetDeploymentResponse200SidekicksItemInfo):
            statuses (Union[Unset, None, str]):  Statuses of engine sidekick servers.
     """

    info: 'StatusGetDeploymentResponse200SidekicksItemInfo'
    statuses: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        info = self.info.to_dict()

        statuses = self.statuses

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "info": info,
        })
        if statuses is not UNSET:
            field_dict["statuses"] = statuses

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.status_get_deployment_response_200_sidekicks_item_info import \
            StatusGetDeploymentResponse200SidekicksItemInfo
        d = src_dict.copy()
        info = StatusGetDeploymentResponse200SidekicksItemInfo.from_dict(d.pop("info"))




        statuses = d.pop("statuses", UNSET)

        status_get_deployment_response_200_sidekicks_item = cls(
            info=info,
            statuses=statuses,
        )

        status_get_deployment_response_200_sidekicks_item.additional_properties = d
        return status_get_deployment_response_200_sidekicks_item

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
