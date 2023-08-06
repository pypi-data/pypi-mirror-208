from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.connections_create_json_body_details import \
      ConnectionsCreateJsonBodyDetails





T = TypeVar("T", bound="ConnectionsCreateJsonBody")


@attr.s(auto_attribs=True)
class ConnectionsCreateJsonBody:
    """  Request to create a new Connection

        Attributes:
            name (str):  Descriptive name for the new connection
            type (str):  The type of connection that can be made
            details (Union[Unset, None, ConnectionsCreateJsonBodyDetails]):  The info needed to make a connection
     """

    name: str
    type: str
    details: Union[Unset, None, 'ConnectionsCreateJsonBodyDetails'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type = self.type
        details: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict() if self.details else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "type": type,
        })
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.connections_create_json_body_details import \
            ConnectionsCreateJsonBodyDetails
        d = src_dict.copy()
        name = d.pop("name")

        type = d.pop("type")

        _details = d.pop("details", UNSET)
        details: Union[Unset, None, ConnectionsCreateJsonBodyDetails]
        if _details is None:
            details = None
        elif isinstance(_details,  Unset):
            details = UNSET
        else:
            details = ConnectionsCreateJsonBodyDetails.from_dict(_details)




        connections_create_json_body = cls(
            name=name,
            type=type,
            details=details,
        )

        connections_create_json_body.additional_properties = d
        return connections_create_json_body

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
