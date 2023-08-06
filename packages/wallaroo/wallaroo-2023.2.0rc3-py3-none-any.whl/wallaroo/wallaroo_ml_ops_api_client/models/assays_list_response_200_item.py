from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.assays_list_response_200_item_baseline_type_0 import \
      AssaysListResponse200ItemBaselineType0
  from ..models.assays_list_response_200_item_baseline_type_1 import \
      AssaysListResponse200ItemBaselineType1
  from ..models.assays_list_response_200_item_baseline_type_2 import \
      AssaysListResponse200ItemBaselineType2
  from ..models.assays_list_response_200_item_summarizer_type_0 import \
      AssaysListResponse200ItemSummarizerType0
  from ..models.assays_list_response_200_item_summarizer_type_1 import \
      AssaysListResponse200ItemSummarizerType1
  from ..models.assays_list_response_200_item_window import \
      AssaysListResponse200ItemWindow





T = TypeVar("T", bound="AssaysListResponse200Item")


@attr.s(auto_attribs=True)
class AssaysListResponse200Item:
    """  Assay definition.

        Attributes:
            id (int):  Assay identifier.
            name (str):  Assay name.
            active (bool):  Flag indicating whether the assay is active.
            status (str):  Assay status.
            alert_threshold (float):  Alert threshold.
            pipeline_id (int):  Pipeline identifier.
            pipeline_name (str):  Pipeline name.
            next_run (str):  Date and time of the next run.
            warning_threshold (Union[Unset, None, float]):  Warning threshold.
            last_run (Union[Unset, None, str]):  Date and time of the last run.
            run_until (Union[Unset, None, str]):  Date and time until which the assay is to run.
            updated_at (Union[Unset, None, str]):  Date and time the assay was last updated.
            baseline (Union['AssaysListResponse200ItemBaselineType0', 'AssaysListResponse200ItemBaselineType1',
                'AssaysListResponse200ItemBaselineType2', None, Unset]):  Options describing the range of inference data used as
                a baseline by the assay
            window (Union[Unset, None, AssaysListResponse200ItemWindow]):  Options describing the time range tested by the
                assay
            summarizer (Union['AssaysListResponse200ItemSummarizerType0', 'AssaysListResponse200ItemSummarizerType1', None,
                Unset]):  Options describing the types of analysis done by the assay
     """

    id: int
    name: str
    active: bool
    status: str
    alert_threshold: float
    pipeline_id: int
    pipeline_name: str
    next_run: str
    warning_threshold: Union[Unset, None, float] = UNSET
    last_run: Union[Unset, None, str] = UNSET
    run_until: Union[Unset, None, str] = UNSET
    updated_at: Union[Unset, None, str] = UNSET
    baseline: Union['AssaysListResponse200ItemBaselineType0', 'AssaysListResponse200ItemBaselineType1', 'AssaysListResponse200ItemBaselineType2', None, Unset] = UNSET
    window: Union[Unset, None, 'AssaysListResponse200ItemWindow'] = UNSET
    summarizer: Union['AssaysListResponse200ItemSummarizerType0', 'AssaysListResponse200ItemSummarizerType1', None, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.assays_list_response_200_item_baseline_type_0 import \
            AssaysListResponse200ItemBaselineType0
        from ..models.assays_list_response_200_item_baseline_type_1 import \
            AssaysListResponse200ItemBaselineType1
        from ..models.assays_list_response_200_item_summarizer_type_0 import \
            AssaysListResponse200ItemSummarizerType0
        id = self.id
        name = self.name
        active = self.active
        status = self.status
        alert_threshold = self.alert_threshold
        pipeline_id = self.pipeline_id
        pipeline_name = self.pipeline_name
        next_run = self.next_run
        warning_threshold = self.warning_threshold
        last_run = self.last_run
        run_until = self.run_until
        updated_at = self.updated_at
        baseline: Union[Dict[str, Any], None, Unset]
        if isinstance(self.baseline, Unset):
            baseline = UNSET
        elif self.baseline is None:
            baseline = None

        elif isinstance(self.baseline, AssaysListResponse200ItemBaselineType0):
            baseline = UNSET
            if not isinstance(self.baseline, Unset):
                baseline = self.baseline.to_dict()

        elif isinstance(self.baseline, AssaysListResponse200ItemBaselineType1):
            baseline = UNSET
            if not isinstance(self.baseline, Unset):
                baseline = self.baseline.to_dict()

        else:
            baseline = UNSET
            if not isinstance(self.baseline, Unset):
                baseline = self.baseline.to_dict()



        window: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.window, Unset):
            window = self.window.to_dict() if self.window else None

        summarizer: Union[Dict[str, Any], None, Unset]
        if isinstance(self.summarizer, Unset):
            summarizer = UNSET
        elif self.summarizer is None:
            summarizer = None

        elif isinstance(self.summarizer, AssaysListResponse200ItemSummarizerType0):
            summarizer = UNSET
            if not isinstance(self.summarizer, Unset):
                summarizer = self.summarizer.to_dict()

        else:
            summarizer = UNSET
            if not isinstance(self.summarizer, Unset):
                summarizer = self.summarizer.to_dict()




        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "active": active,
            "status": status,
            "alert_threshold": alert_threshold,
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "next_run": next_run,
        })
        if warning_threshold is not UNSET:
            field_dict["warning_threshold"] = warning_threshold
        if last_run is not UNSET:
            field_dict["last_run"] = last_run
        if run_until is not UNSET:
            field_dict["run_until"] = run_until
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if baseline is not UNSET:
            field_dict["baseline"] = baseline
        if window is not UNSET:
            field_dict["window"] = window
        if summarizer is not UNSET:
            field_dict["summarizer"] = summarizer

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_list_response_200_item_baseline_type_0 import \
            AssaysListResponse200ItemBaselineType0
        from ..models.assays_list_response_200_item_baseline_type_1 import \
            AssaysListResponse200ItemBaselineType1
        from ..models.assays_list_response_200_item_baseline_type_2 import \
            AssaysListResponse200ItemBaselineType2
        from ..models.assays_list_response_200_item_summarizer_type_0 import \
            AssaysListResponse200ItemSummarizerType0
        from ..models.assays_list_response_200_item_summarizer_type_1 import \
            AssaysListResponse200ItemSummarizerType1
        from ..models.assays_list_response_200_item_window import \
            AssaysListResponse200ItemWindow
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        active = d.pop("active")

        status = d.pop("status")

        alert_threshold = d.pop("alert_threshold")

        pipeline_id = d.pop("pipeline_id")

        pipeline_name = d.pop("pipeline_name")

        next_run = d.pop("next_run")

        warning_threshold = d.pop("warning_threshold", UNSET)

        last_run = d.pop("last_run", UNSET)

        run_until = d.pop("run_until", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        def _parse_baseline(data: object) -> Union['AssaysListResponse200ItemBaselineType0', 'AssaysListResponse200ItemBaselineType1', 'AssaysListResponse200ItemBaselineType2', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _baseline_type_0 = data
                baseline_type_0: Union[Unset, AssaysListResponse200ItemBaselineType0]
                if isinstance(_baseline_type_0,  Unset):
                    baseline_type_0 = UNSET
                else:
                    baseline_type_0 = AssaysListResponse200ItemBaselineType0.from_dict(_baseline_type_0)



                return baseline_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _baseline_type_1 = data
                baseline_type_1: Union[Unset, AssaysListResponse200ItemBaselineType1]
                if isinstance(_baseline_type_1,  Unset):
                    baseline_type_1 = UNSET
                else:
                    baseline_type_1 = AssaysListResponse200ItemBaselineType1.from_dict(_baseline_type_1)



                return baseline_type_1
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            _baseline_type_2 = data
            baseline_type_2: Union[Unset, AssaysListResponse200ItemBaselineType2]
            if isinstance(_baseline_type_2,  Unset):
                baseline_type_2 = UNSET
            else:
                baseline_type_2 = AssaysListResponse200ItemBaselineType2.from_dict(_baseline_type_2)



            return baseline_type_2

        baseline = _parse_baseline(d.pop("baseline", UNSET))


        _window = d.pop("window", UNSET)
        window: Union[Unset, None, AssaysListResponse200ItemWindow]
        if _window is None:
            window = None
        elif isinstance(_window,  Unset):
            window = UNSET
        else:
            window = AssaysListResponse200ItemWindow.from_dict(_window)




        def _parse_summarizer(data: object) -> Union['AssaysListResponse200ItemSummarizerType0', 'AssaysListResponse200ItemSummarizerType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _summarizer_type_0 = data
                summarizer_type_0: Union[Unset, AssaysListResponse200ItemSummarizerType0]
                if isinstance(_summarizer_type_0,  Unset):
                    summarizer_type_0 = UNSET
                else:
                    summarizer_type_0 = AssaysListResponse200ItemSummarizerType0.from_dict(_summarizer_type_0)



                return summarizer_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            _summarizer_type_1 = data
            summarizer_type_1: Union[Unset, AssaysListResponse200ItemSummarizerType1]
            if isinstance(_summarizer_type_1,  Unset):
                summarizer_type_1 = UNSET
            else:
                summarizer_type_1 = AssaysListResponse200ItemSummarizerType1.from_dict(_summarizer_type_1)



            return summarizer_type_1

        summarizer = _parse_summarizer(d.pop("summarizer", UNSET))


        assays_list_response_200_item = cls(
            id=id,
            name=name,
            active=active,
            status=status,
            alert_threshold=alert_threshold,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            next_run=next_run,
            warning_threshold=warning_threshold,
            last_run=last_run,
            run_until=run_until,
            updated_at=updated_at,
            baseline=baseline,
            window=window,
            summarizer=summarizer,
        )

        assays_list_response_200_item.additional_properties = d
        return assays_list_response_200_item

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
