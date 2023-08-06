from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar

import attr

if TYPE_CHECKING:
  from ..models.users_query_response_200_users_additional_property import \
      UsersQueryResponse200UsersAdditionalProperty





T = TypeVar("T", bound="UsersQueryResponse200Users")


@attr.s(auto_attribs=True)
class UsersQueryResponse200Users:
    """  User details keyed by User ID.

     """

    additional_properties: Dict[str, Optional['UsersQueryResponse200UsersAdditionalProperty']] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pass
        
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict() if prop else None

        field_dict.update({
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.users_query_response_200_users_additional_property import \
            UsersQueryResponse200UsersAdditionalProperty
        d = src_dict.copy()
        users_query_response_200_users = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            _additional_property = prop_dict
            additional_property: Optional[UsersQueryResponse200UsersAdditionalProperty]
            if _additional_property is None:
                additional_property = None
            else:
                additional_property = UsersQueryResponse200UsersAdditionalProperty.from_dict(_additional_property)



            additional_properties[prop_name] = additional_property

        users_query_response_200_users.additional_properties = additional_properties
        return users_query_response_200_users

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Optional['UsersQueryResponse200UsersAdditionalProperty']:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Optional['UsersQueryResponse200UsersAdditionalProperty']) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
