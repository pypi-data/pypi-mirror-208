from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
  from ..models.assays_list_response_200_item_baseline_type_2_sliding import \
      AssaysListResponse200ItemBaselineType2Sliding





T = TypeVar("T", bound="AssaysListResponse200ItemBaselineType2")


@attr.s(auto_attribs=True)
class AssaysListResponse200ItemBaselineType2:
    """ 
        Attributes:
            sliding (AssaysListResponse200ItemBaselineType2Sliding):
     """

    sliding: 'AssaysListResponse200ItemBaselineType2Sliding'
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        sliding = self.sliding.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "Sliding": sliding,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_list_response_200_item_baseline_type_2_sliding import \
            AssaysListResponse200ItemBaselineType2Sliding
        d = src_dict.copy()
        sliding = AssaysListResponse200ItemBaselineType2Sliding.from_dict(d.pop("Sliding"))




        assays_list_response_200_item_baseline_type_2 = cls(
            sliding=sliding,
        )

        assays_list_response_200_item_baseline_type_2.additional_properties = d
        return assays_list_response_200_item_baseline_type_2

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
