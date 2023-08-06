from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExplainabilityCreateRequestJsonBodyWindowConfig")


@attr.s(auto_attribs=True)
class ExplainabilityCreateRequestJsonBodyWindowConfig:
    """  Specifies if start, end and num samples for the a window of data.

        Attributes:
            start (Union[Unset, None, str]):  The start of this window of data
            end (Union[Unset, None, str]):  The end of this window of data
            num_samples (Union[Unset, None, int]):  The number of inference samples to use
     """

    start: Union[Unset, None, str] = UNSET
    end: Union[Unset, None, str] = UNSET
    num_samples: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        start = self.start
        end = self.end
        num_samples = self.num_samples

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if num_samples is not UNSET:
            field_dict["num_samples"] = num_samples

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start = d.pop("start", UNSET)

        end = d.pop("end", UNSET)

        num_samples = d.pop("num_samples", UNSET)

        explainability_create_request_json_body_window_config = cls(
            start=start,
            end=end,
            num_samples=num_samples,
        )

        explainability_create_request_json_body_window_config.additional_properties = d
        return explainability_create_request_json_body_window_config

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
