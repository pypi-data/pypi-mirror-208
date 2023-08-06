from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="AssaysFilterResponse200ItemBaselineType2Sliding")


@attr.s(auto_attribs=True)
class AssaysFilterResponse200ItemBaselineType2Sliding:
    """ 
        Attributes:
            pipeline (str):
            model (str):
            width (str):
            offset (str):
     """

    pipeline: str
    model: str
    width: str
    offset: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline = self.pipeline
        model = self.model
        width = self.width
        offset = self.offset

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline": pipeline,
            "model": model,
            "width": width,
            "offset": offset,
        })

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline = d.pop("pipeline")

        model = d.pop("model")

        width = d.pop("width")

        offset = d.pop("offset")

        assays_filter_response_200_item_baseline_type_2_sliding = cls(
            pipeline=pipeline,
            model=model,
            width=width,
            offset=offset,
        )

        assays_filter_response_200_item_baseline_type_2_sliding.additional_properties = d
        return assays_filter_response_200_item_baseline_type_2_sliding

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
