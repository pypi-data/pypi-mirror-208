from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
  from ..models.assays_filter_response_200_item_baseline_type_0_user_provided import \
      AssaysFilterResponse200ItemBaselineType0UserProvided





T = TypeVar("T", bound="AssaysFilterResponse200ItemBaselineType0")


@attr.s(auto_attribs=True)
class AssaysFilterResponse200ItemBaselineType0:
    """ 
        Attributes:
            user_provided (AssaysFilterResponse200ItemBaselineType0UserProvided):
     """

    user_provided: 'AssaysFilterResponse200ItemBaselineType0UserProvided'
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        user_provided = self.user_provided.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "UserProvided": user_provided,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_filter_response_200_item_baseline_type_0_user_provided import \
            AssaysFilterResponse200ItemBaselineType0UserProvided
        d = src_dict.copy()
        user_provided = AssaysFilterResponse200ItemBaselineType0UserProvided.from_dict(d.pop("UserProvided"))




        assays_filter_response_200_item_baseline_type_0 = cls(
            user_provided=user_provided,
        )

        assays_filter_response_200_item_baseline_type_0.additional_properties = d
        return assays_filter_response_200_item_baseline_type_0

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
