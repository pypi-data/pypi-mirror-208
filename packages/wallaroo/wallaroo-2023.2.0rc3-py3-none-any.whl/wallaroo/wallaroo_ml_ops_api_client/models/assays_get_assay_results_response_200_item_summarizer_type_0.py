from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.assays_get_assay_results_response_200_item_summarizer_type_0_aggregation import \
    AssaysGetAssayResultsResponse200ItemSummarizerType0Aggregation
from ..models.assays_get_assay_results_response_200_item_summarizer_type_0_bin_mode import \
    AssaysGetAssayResultsResponse200ItemSummarizerType0BinMode
from ..models.assays_get_assay_results_response_200_item_summarizer_type_0_metric import \
    AssaysGetAssayResultsResponse200ItemSummarizerType0Metric
from ..models.assays_get_assay_results_response_200_item_summarizer_type_0_type import \
    AssaysGetAssayResultsResponse200ItemSummarizerType0Type
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssaysGetAssayResultsResponse200ItemSummarizerType0")


@attr.s(auto_attribs=True)
class AssaysGetAssayResultsResponse200ItemSummarizerType0:
    """  Defines the summarizer/test we want to conduct

        Attributes:
            bin_mode (AssaysGetAssayResultsResponse200ItemSummarizerType0BinMode):
            aggregation (AssaysGetAssayResultsResponse200ItemSummarizerType0Aggregation):
            metric (AssaysGetAssayResultsResponse200ItemSummarizerType0Metric):  How we calculate the score between two
                histograms/vecs.  Add pct_diff and sum_pct_diff?
            num_bins (int):
            type (AssaysGetAssayResultsResponse200ItemSummarizerType0Type):
            bin_weights (Union[Unset, None, List[float]]):
            provided_edges (Union[Unset, None, List[float]]):
     """

    bin_mode: AssaysGetAssayResultsResponse200ItemSummarizerType0BinMode
    aggregation: AssaysGetAssayResultsResponse200ItemSummarizerType0Aggregation
    metric: AssaysGetAssayResultsResponse200ItemSummarizerType0Metric
    num_bins: int
    type: AssaysGetAssayResultsResponse200ItemSummarizerType0Type
    bin_weights: Union[Unset, None, List[float]] = UNSET
    provided_edges: Union[Unset, None, List[float]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        bin_mode = self.bin_mode.value

        aggregation = self.aggregation.value

        metric = self.metric.value

        num_bins = self.num_bins
        type = self.type.value

        bin_weights: Union[Unset, None, List[float]] = UNSET
        if not isinstance(self.bin_weights, Unset):
            if self.bin_weights is None:
                bin_weights = None
            else:
                bin_weights = self.bin_weights




        provided_edges: Union[Unset, None, List[float]] = UNSET
        if not isinstance(self.provided_edges, Unset):
            if self.provided_edges is None:
                provided_edges = None
            else:
                provided_edges = self.provided_edges





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "bin_mode": bin_mode,
            "aggregation": aggregation,
            "metric": metric,
            "num_bins": num_bins,
            "type": type,
        })
        if bin_weights is not UNSET:
            field_dict["bin_weights"] = bin_weights
        if provided_edges is not UNSET:
            field_dict["provided_edges"] = provided_edges

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bin_mode = AssaysGetAssayResultsResponse200ItemSummarizerType0BinMode(d.pop("bin_mode"))




        aggregation = AssaysGetAssayResultsResponse200ItemSummarizerType0Aggregation(d.pop("aggregation"))




        metric = AssaysGetAssayResultsResponse200ItemSummarizerType0Metric(d.pop("metric"))




        num_bins = d.pop("num_bins")

        type = AssaysGetAssayResultsResponse200ItemSummarizerType0Type(d.pop("type"))




        bin_weights = cast(List[float], d.pop("bin_weights", UNSET))


        provided_edges = cast(List[float], d.pop("provided_edges", UNSET))


        assays_get_assay_results_response_200_item_summarizer_type_0 = cls(
            bin_mode=bin_mode,
            aggregation=aggregation,
            metric=metric,
            num_bins=num_bins,
            type=type,
            bin_weights=bin_weights,
            provided_edges=provided_edges,
        )

        assays_get_assay_results_response_200_item_summarizer_type_0.additional_properties = d
        return assays_get_assay_results_response_200_item_summarizer_type_0

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
