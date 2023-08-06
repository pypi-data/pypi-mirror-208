import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.connections_get_by_id_response_200_details import \
      ConnectionsGetByIdResponse200Details





T = TypeVar("T", bound="ConnectionsGetByIdResponse200")


@attr.s(auto_attribs=True)
class ConnectionsGetByIdResponse200:
    """  Response to fetching a Connection by its Id

        Attributes:
            id (str):
            name (str):
            type (str):
            created_at (datetime.datetime):
            workspace_names (List[str]):
            details (Union[Unset, None, ConnectionsGetByIdResponse200Details]):
     """

    id: str
    name: str
    type: str
    created_at: datetime.datetime
    workspace_names: List[str]
    details: Union[Unset, None, 'ConnectionsGetByIdResponse200Details'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        type = self.type
        created_at = self.created_at.isoformat()

        workspace_names = self.workspace_names




        details: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict() if self.details else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "type": type,
            "created_at": created_at,
            "workspace_names": workspace_names,
        })
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.connections_get_by_id_response_200_details import \
            ConnectionsGetByIdResponse200Details
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        type = d.pop("type")

        created_at = isoparse(d.pop("created_at"))




        workspace_names = cast(List[str], d.pop("workspace_names"))


        _details = d.pop("details", UNSET)
        details: Union[Unset, None, ConnectionsGetByIdResponse200Details]
        if _details is None:
            details = None
        elif isinstance(_details,  Unset):
            details = UNSET
        else:
            details = ConnectionsGetByIdResponse200Details.from_dict(_details)




        connections_get_by_id_response_200 = cls(
            id=id,
            name=name,
            type=type,
            created_at=created_at,
            workspace_names=workspace_names,
            details=details,
        )

        connections_get_by_id_response_200.additional_properties = d
        return connections_get_by_id_response_200

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
