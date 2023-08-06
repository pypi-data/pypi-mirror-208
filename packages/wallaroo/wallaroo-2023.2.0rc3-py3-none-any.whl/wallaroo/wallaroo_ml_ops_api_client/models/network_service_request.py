from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.network_service_request_json import NetworkServiceRequestJson





T = TypeVar("T", bound="NetworkServiceRequest")


@attr.s(auto_attribs=True)
class NetworkServiceRequest:
    """ 
        Attributes:
            json (NetworkServiceRequestJson):
            name (str):
            orch_id (str):
            service_name (str):
            service_port (int):
            service_protocol (str):
            workspace_id (int):
            timeout (Union[Unset, None, int]):
     """

    json: 'NetworkServiceRequestJson'
    name: str
    orch_id: str
    service_name: str
    service_port: int
    service_protocol: str
    workspace_id: int
    timeout: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        json = self.json.to_dict()

        name = self.name
        orch_id = self.orch_id
        service_name = self.service_name
        service_port = self.service_port
        service_protocol = self.service_protocol
        workspace_id = self.workspace_id
        timeout = self.timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "json": json,
            "name": name,
            "orch_id": orch_id,
            "service_name": service_name,
            "service_port": service_port,
            "service_protocol": service_protocol,
            "workspace_id": workspace_id,
        })
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.network_service_request_json import \
            NetworkServiceRequestJson
        d = src_dict.copy()
        json = NetworkServiceRequestJson.from_dict(d.pop("json"))




        name = d.pop("name")

        orch_id = d.pop("orch_id")

        service_name = d.pop("service_name")

        service_port = d.pop("service_port")

        service_protocol = d.pop("service_protocol")

        workspace_id = d.pop("workspace_id")

        timeout = d.pop("timeout", UNSET)

        network_service_request = cls(
            json=json,
            name=name,
            orch_id=orch_id,
            service_name=service_name,
            service_port=service_port,
            service_protocol=service_protocol,
            workspace_id=workspace_id,
            timeout=timeout,
        )

        network_service_request.additional_properties = d
        return network_service_request

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
