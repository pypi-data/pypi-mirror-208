import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssaysCreateJsonBodyWindow")


@attr.s(auto_attribs=True)
class AssaysCreateJsonBodyWindow:
    """  Assay window.

        Attributes:
            pipeline (str):  Pipeline name.
            model (str):  Model name.
            width (str):  Window width.
            start (Union[Unset, None, datetime.datetime]):  Window start definition.
            interval (Union[Unset, None, str]):  Window interval.
     """

    pipeline: str
    model: str
    width: str
    start: Union[Unset, None, datetime.datetime] = UNSET
    interval: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline = self.pipeline
        model = self.model
        width = self.width
        start: Union[Unset, None, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat() if self.start else None

        interval = self.interval

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline": pipeline,
            "model": model,
            "width": width,
        })
        if start is not UNSET:
            field_dict["start"] = start
        if interval is not UNSET:
            field_dict["interval"] = interval

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline = d.pop("pipeline")

        model = d.pop("model")

        width = d.pop("width")

        _start = d.pop("start", UNSET)
        start: Union[Unset, None, datetime.datetime]
        if _start is None:
            start = None
        elif isinstance(_start,  Unset):
            start = UNSET
        else:
            start = isoparse(_start)




        interval = d.pop("interval", UNSET)

        assays_create_json_body_window = cls(
            pipeline=pipeline,
            model=model,
            width=width,
            start=start,
            interval=interval,
        )

        assays_create_json_body_window.additional_properties = d
        return assays_create_json_body_window

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
