from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.oneshot_request_json import OneshotRequestJson





T = TypeVar("T", bound="OneshotRequest")


@attr.s(auto_attribs=True)
class OneshotRequest:
    """ 
        Attributes:
            json (OneshotRequestJson):
            orch_id (str):
            workspace_id (int):
            name (Union[Unset, None, str]):
            timeout (Union[Unset, None, int]):
     """

    json: 'OneshotRequestJson'
    orch_id: str
    workspace_id: int
    name: Union[Unset, None, str] = UNSET
    timeout: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        json = self.json.to_dict()

        orch_id = self.orch_id
        workspace_id = self.workspace_id
        name = self.name
        timeout = self.timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "json": json,
            "orch_id": orch_id,
            "workspace_id": workspace_id,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.oneshot_request_json import OneshotRequestJson
        d = src_dict.copy()
        json = OneshotRequestJson.from_dict(d.pop("json"))




        orch_id = d.pop("orch_id")

        workspace_id = d.pop("workspace_id")

        name = d.pop("name", UNSET)

        timeout = d.pop("timeout", UNSET)

        oneshot_request = cls(
            json=json,
            orch_id=orch_id,
            workspace_id=workspace_id,
            name=name,
            timeout=timeout,
        )

        oneshot_request.additional_properties = d
        return oneshot_request

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
