import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.assays_get_assay_results_response_200_item_window_summary_aggregation import \
    AssaysGetAssayResultsResponse200ItemWindowSummaryAggregation
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssaysGetAssayResultsResponse200ItemWindowSummary")


@attr.s(auto_attribs=True)
class AssaysGetAssayResultsResponse200ItemWindowSummary:
    """  Result from summarizing one sample collection.

        Attributes:
            count (int):
            min_ (float):
            max_ (float):
            mean (float):
            median (float):
            std (float):  Standard deviation.
            edges (List[float]):
            edge_names (List[str]):
            aggregated_values (List[float]):
            aggregation (AssaysGetAssayResultsResponse200ItemWindowSummaryAggregation):
            start (Union[Unset, None, datetime.datetime]):
            end (Union[Unset, None, datetime.datetime]):
     """

    count: int
    min_: float
    max_: float
    mean: float
    median: float
    std: float
    edges: List[float]
    edge_names: List[str]
    aggregated_values: List[float]
    aggregation: AssaysGetAssayResultsResponse200ItemWindowSummaryAggregation
    start: Union[Unset, None, datetime.datetime] = UNSET
    end: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        count = self.count
        min_ = self.min_
        max_ = self.max_
        mean = self.mean
        median = self.median
        std = self.std
        edges = self.edges




        edge_names = self.edge_names




        aggregated_values = self.aggregated_values




        aggregation = self.aggregation.value

        start: Union[Unset, None, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat() if self.start else None

        end: Union[Unset, None, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat() if self.end else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "count": count,
            "min": min_,
            "max": max_,
            "mean": mean,
            "median": median,
            "std": std,
            "edges": edges,
            "edge_names": edge_names,
            "aggregated_values": aggregated_values,
            "aggregation": aggregation,
        })
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        count = d.pop("count")

        min_ = d.pop("min")

        max_ = d.pop("max")

        mean = d.pop("mean")

        median = d.pop("median")

        std = d.pop("std")

        edges = cast(List[float], d.pop("edges"))


        edge_names = cast(List[str], d.pop("edge_names"))


        aggregated_values = cast(List[float], d.pop("aggregated_values"))


        aggregation = AssaysGetAssayResultsResponse200ItemWindowSummaryAggregation(d.pop("aggregation"))




        _start = d.pop("start", UNSET)
        start: Union[Unset, None, datetime.datetime]
        if _start is None:
            start = None
        elif isinstance(_start,  Unset):
            start = UNSET
        else:
            start = isoparse(_start)




        _end = d.pop("end", UNSET)
        end: Union[Unset, None, datetime.datetime]
        if _end is None:
            end = None
        elif isinstance(_end,  Unset):
            end = UNSET
        else:
            end = isoparse(_end)




        assays_get_assay_results_response_200_item_window_summary = cls(
            count=count,
            min_=min_,
            max_=max_,
            mean=mean,
            median=median,
            std=std,
            edges=edges,
            edge_names=edge_names,
            aggregated_values=aggregated_values,
            aggregation=aggregation,
            start=start,
            end=end,
        )

        assays_get_assay_results_response_200_item_window_summary.additional_properties = d
        return assays_get_assay_results_response_200_item_window_summary

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
