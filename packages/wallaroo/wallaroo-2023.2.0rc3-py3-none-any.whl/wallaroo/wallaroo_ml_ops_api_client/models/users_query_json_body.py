from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsersQueryJsonBody")


@attr.s(auto_attribs=True)
class UsersQueryJsonBody:
    """  Specifies which users to query.

        Attributes:
            user_ids (Union[Unset, None, List[str]]):  Optional list of user IDs to return.
     """

    user_ids: Union[Unset, None, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        user_ids: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.user_ids, Unset):
            if self.user_ids is None:
                user_ids = None
            else:
                user_ids = self.user_ids





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if user_ids is not UNSET:
            field_dict["user_ids"] = user_ids

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_ids = cast(List[str], d.pop("user_ids", UNSET))


        users_query_json_body = cls(
            user_ids=user_ids,
        )

        users_query_json_body.additional_properties = d
        return users_query_json_body

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
