import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.assays_get_assay_results_response_200_item_status import \
    AssaysGetAssayResultsResponse200ItemStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.assays_get_assay_results_response_200_item_baseline_summary import \
      AssaysGetAssayResultsResponse200ItemBaselineSummary
  from ..models.assays_get_assay_results_response_200_item_summarizer_type_0 import \
      AssaysGetAssayResultsResponse200ItemSummarizerType0
  from ..models.assays_get_assay_results_response_200_item_summarizer_type_1 import \
      AssaysGetAssayResultsResponse200ItemSummarizerType1
  from ..models.assays_get_assay_results_response_200_item_window_summary import \
      AssaysGetAssayResultsResponse200ItemWindowSummary





T = TypeVar("T", bound="AssaysGetAssayResultsResponse200Item")


@attr.s(auto_attribs=True)
class AssaysGetAssayResultsResponse200Item:
    """ 
        Attributes:
            window_start (datetime.datetime):
            analyzed_at (datetime.datetime):
            elapsed_millis (int):
            iopath (str):
            baseline_summary (AssaysGetAssayResultsResponse200ItemBaselineSummary):  Result from summarizing one sample
                collection.
            window_summary (AssaysGetAssayResultsResponse200ItemWindowSummary):  Result from summarizing one sample
                collection.
            alert_threshold (float):
            score (float):
            scores (List[float]):
            summarizer (Union['AssaysGetAssayResultsResponse200ItemSummarizerType0',
                'AssaysGetAssayResultsResponse200ItemSummarizerType1']):
            status (AssaysGetAssayResultsResponse200ItemStatus):
            id (Union[Unset, None, int]):
            assay_id (Union[Unset, None, int]):
            pipeline_id (Union[Unset, None, int]):
            warning_threshold (Union[Unset, None, float]):
            bin_index (Union[Unset, None, int]):
            created_at (Union[Unset, None, datetime.datetime]):
     """

    window_start: datetime.datetime
    analyzed_at: datetime.datetime
    elapsed_millis: int
    iopath: str
    baseline_summary: 'AssaysGetAssayResultsResponse200ItemBaselineSummary'
    window_summary: 'AssaysGetAssayResultsResponse200ItemWindowSummary'
    alert_threshold: float
    score: float
    scores: List[float]
    summarizer: Union['AssaysGetAssayResultsResponse200ItemSummarizerType0', 'AssaysGetAssayResultsResponse200ItemSummarizerType1']
    status: AssaysGetAssayResultsResponse200ItemStatus
    id: Union[Unset, None, int] = UNSET
    assay_id: Union[Unset, None, int] = UNSET
    pipeline_id: Union[Unset, None, int] = UNSET
    warning_threshold: Union[Unset, None, float] = UNSET
    bin_index: Union[Unset, None, int] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.assays_get_assay_results_response_200_item_summarizer_type_0 import \
            AssaysGetAssayResultsResponse200ItemSummarizerType0
        window_start = self.window_start.isoformat()

        analyzed_at = self.analyzed_at.isoformat()

        elapsed_millis = self.elapsed_millis
        iopath = self.iopath
        baseline_summary = self.baseline_summary.to_dict()

        window_summary = self.window_summary.to_dict()

        alert_threshold = self.alert_threshold
        score = self.score
        scores = self.scores




        summarizer: Dict[str, Any]

        if isinstance(self.summarizer, AssaysGetAssayResultsResponse200ItemSummarizerType0):
            summarizer = self.summarizer.to_dict()

        else:
            summarizer = self.summarizer.to_dict()



        status = self.status.value

        id = self.id
        assay_id = self.assay_id
        pipeline_id = self.pipeline_id
        warning_threshold = self.warning_threshold
        bin_index = self.bin_index
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "window_start": window_start,
            "analyzed_at": analyzed_at,
            "elapsed_millis": elapsed_millis,
            "iopath": iopath,
            "baseline_summary": baseline_summary,
            "window_summary": window_summary,
            "alert_threshold": alert_threshold,
            "score": score,
            "scores": scores,
            "summarizer": summarizer,
            "status": status,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if assay_id is not UNSET:
            field_dict["assay_id"] = assay_id
        if pipeline_id is not UNSET:
            field_dict["pipeline_id"] = pipeline_id
        if warning_threshold is not UNSET:
            field_dict["warning_threshold"] = warning_threshold
        if bin_index is not UNSET:
            field_dict["bin_index"] = bin_index
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_get_assay_results_response_200_item_baseline_summary import \
            AssaysGetAssayResultsResponse200ItemBaselineSummary
        from ..models.assays_get_assay_results_response_200_item_summarizer_type_0 import \
            AssaysGetAssayResultsResponse200ItemSummarizerType0
        from ..models.assays_get_assay_results_response_200_item_summarizer_type_1 import \
            AssaysGetAssayResultsResponse200ItemSummarizerType1
        from ..models.assays_get_assay_results_response_200_item_window_summary import \
            AssaysGetAssayResultsResponse200ItemWindowSummary
        d = src_dict.copy()
        window_start = isoparse(d.pop("window_start"))




        analyzed_at = isoparse(d.pop("analyzed_at"))




        elapsed_millis = d.pop("elapsed_millis")

        iopath = d.pop("iopath")

        baseline_summary = AssaysGetAssayResultsResponse200ItemBaselineSummary.from_dict(d.pop("baseline_summary"))




        window_summary = AssaysGetAssayResultsResponse200ItemWindowSummary.from_dict(d.pop("window_summary"))




        alert_threshold = d.pop("alert_threshold")

        score = d.pop("score")

        scores = cast(List[float], d.pop("scores"))


        def _parse_summarizer(data: object) -> Union['AssaysGetAssayResultsResponse200ItemSummarizerType0', 'AssaysGetAssayResultsResponse200ItemSummarizerType1']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                summarizer_type_0 = AssaysGetAssayResultsResponse200ItemSummarizerType0.from_dict(data)



                return summarizer_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            summarizer_type_1 = AssaysGetAssayResultsResponse200ItemSummarizerType1.from_dict(data)



            return summarizer_type_1

        summarizer = _parse_summarizer(d.pop("summarizer"))


        status = AssaysGetAssayResultsResponse200ItemStatus(d.pop("status"))




        id = d.pop("id", UNSET)

        assay_id = d.pop("assay_id", UNSET)

        pipeline_id = d.pop("pipeline_id", UNSET)

        warning_threshold = d.pop("warning_threshold", UNSET)

        bin_index = d.pop("bin_index", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, None, datetime.datetime]
        if _created_at is None:
            created_at = None
        elif isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        assays_get_assay_results_response_200_item = cls(
            window_start=window_start,
            analyzed_at=analyzed_at,
            elapsed_millis=elapsed_millis,
            iopath=iopath,
            baseline_summary=baseline_summary,
            window_summary=window_summary,
            alert_threshold=alert_threshold,
            score=score,
            scores=scores,
            summarizer=summarizer,
            status=status,
            id=id,
            assay_id=assay_id,
            pipeline_id=pipeline_id,
            warning_threshold=warning_threshold,
            bin_index=bin_index,
            created_at=created_at,
        )

        assays_get_assay_results_response_200_item.additional_properties = d
        return assays_get_assay_results_response_200_item

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
