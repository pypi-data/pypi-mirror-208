import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.assays_create_json_body_baseline_type_0 import \
      AssaysCreateJsonBodyBaselineType0
  from ..models.assays_create_json_body_baseline_type_1 import \
      AssaysCreateJsonBodyBaselineType1
  from ..models.assays_create_json_body_baseline_type_2 import \
      AssaysCreateJsonBodyBaselineType2
  from ..models.assays_create_json_body_summarizer_type_0 import \
      AssaysCreateJsonBodySummarizerType0
  from ..models.assays_create_json_body_summarizer_type_1 import \
      AssaysCreateJsonBodySummarizerType1
  from ..models.assays_create_json_body_window import \
      AssaysCreateJsonBodyWindow





T = TypeVar("T", bound="AssaysCreateJsonBody")


@attr.s(auto_attribs=True)
class AssaysCreateJsonBody:
    """  Request to create an assay.

        Attributes:
            name (str):
            pipeline_id (int):
            pipeline_name (str):
            active (bool):
            status (str):
            iopath (str):
            baseline (Union['AssaysCreateJsonBodyBaselineType0', 'AssaysCreateJsonBodyBaselineType1',
                'AssaysCreateJsonBodyBaselineType2']):
            window (AssaysCreateJsonBodyWindow):  Assay window.
            summarizer (Union['AssaysCreateJsonBodySummarizerType0', 'AssaysCreateJsonBodySummarizerType1']):
            alert_threshold (float):
            created_at (datetime.datetime):
            workspace_id (int):
            id (Union[Unset, None, int]):
            warning_threshold (Union[Unset, None, float]):
            last_window_start (Union[Unset, None, datetime.datetime]):
            run_until (Union[Unset, None, datetime.datetime]):
            last_run (Union[Unset, None, datetime.datetime]):
     """

    name: str
    pipeline_id: int
    pipeline_name: str
    active: bool
    status: str
    iopath: str
    baseline: Union['AssaysCreateJsonBodyBaselineType0', 'AssaysCreateJsonBodyBaselineType1', 'AssaysCreateJsonBodyBaselineType2']
    window: 'AssaysCreateJsonBodyWindow'
    summarizer: Union['AssaysCreateJsonBodySummarizerType0', 'AssaysCreateJsonBodySummarizerType1']
    alert_threshold: float
    created_at: datetime.datetime
    workspace_id: int
    id: Union[Unset, None, int] = UNSET
    warning_threshold: Union[Unset, None, float] = UNSET
    last_window_start: Union[Unset, None, datetime.datetime] = UNSET
    run_until: Union[Unset, None, datetime.datetime] = UNSET
    last_run: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        from ..models.assays_create_json_body_baseline_type_0 import \
            AssaysCreateJsonBodyBaselineType0
        from ..models.assays_create_json_body_baseline_type_1 import \
            AssaysCreateJsonBodyBaselineType1
        from ..models.assays_create_json_body_summarizer_type_0 import \
            AssaysCreateJsonBodySummarizerType0
        name = self.name
        pipeline_id = self.pipeline_id
        pipeline_name = self.pipeline_name
        active = self.active
        status = self.status
        iopath = self.iopath
        baseline: Dict[str, Any]

        if isinstance(self.baseline, AssaysCreateJsonBodyBaselineType0):
            baseline = self.baseline.to_dict()

        elif isinstance(self.baseline, AssaysCreateJsonBodyBaselineType1):
            baseline = self.baseline.to_dict()

        else:
            baseline = self.baseline.to_dict()



        window = self.window.to_dict()

        summarizer: Dict[str, Any]

        if isinstance(self.summarizer, AssaysCreateJsonBodySummarizerType0):
            summarizer = self.summarizer.to_dict()

        else:
            summarizer = self.summarizer.to_dict()



        alert_threshold = self.alert_threshold
        created_at = self.created_at.isoformat()

        workspace_id = self.workspace_id
        id = self.id
        warning_threshold = self.warning_threshold
        last_window_start: Union[Unset, None, str] = UNSET
        if not isinstance(self.last_window_start, Unset):
            last_window_start = self.last_window_start.isoformat() if self.last_window_start else None

        run_until: Union[Unset, None, str] = UNSET
        if not isinstance(self.run_until, Unset):
            run_until = self.run_until.isoformat() if self.run_until else None

        last_run: Union[Unset, None, str] = UNSET
        if not isinstance(self.last_run, Unset):
            last_run = self.last_run.isoformat() if self.last_run else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "active": active,
            "status": status,
            "iopath": iopath,
            "baseline": baseline,
            "window": window,
            "summarizer": summarizer,
            "alert_threshold": alert_threshold,
            "created_at": created_at,
            "workspace_id": workspace_id,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if warning_threshold is not UNSET:
            field_dict["warning_threshold"] = warning_threshold
        if last_window_start is not UNSET:
            field_dict["last_window_start"] = last_window_start
        if run_until is not UNSET:
            field_dict["run_until"] = run_until
        if last_run is not UNSET:
            field_dict["last_run"] = last_run

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_create_json_body_baseline_type_0 import \
            AssaysCreateJsonBodyBaselineType0
        from ..models.assays_create_json_body_baseline_type_1 import \
            AssaysCreateJsonBodyBaselineType1
        from ..models.assays_create_json_body_baseline_type_2 import \
            AssaysCreateJsonBodyBaselineType2
        from ..models.assays_create_json_body_summarizer_type_0 import \
            AssaysCreateJsonBodySummarizerType0
        from ..models.assays_create_json_body_summarizer_type_1 import \
            AssaysCreateJsonBodySummarizerType1
        from ..models.assays_create_json_body_window import \
            AssaysCreateJsonBodyWindow
        d = src_dict.copy()
        name = d.pop("name")

        pipeline_id = d.pop("pipeline_id")

        pipeline_name = d.pop("pipeline_name")

        active = d.pop("active")

        status = d.pop("status")

        iopath = d.pop("iopath")

        def _parse_baseline(data: object) -> Union['AssaysCreateJsonBodyBaselineType0', 'AssaysCreateJsonBodyBaselineType1', 'AssaysCreateJsonBodyBaselineType2']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                baseline_type_0 = AssaysCreateJsonBodyBaselineType0.from_dict(data)



                return baseline_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                baseline_type_1 = AssaysCreateJsonBodyBaselineType1.from_dict(data)



                return baseline_type_1
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            baseline_type_2 = AssaysCreateJsonBodyBaselineType2.from_dict(data)



            return baseline_type_2

        baseline = _parse_baseline(d.pop("baseline"))


        window = AssaysCreateJsonBodyWindow.from_dict(d.pop("window"))




        def _parse_summarizer(data: object) -> Union['AssaysCreateJsonBodySummarizerType0', 'AssaysCreateJsonBodySummarizerType1']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                summarizer_type_0 = AssaysCreateJsonBodySummarizerType0.from_dict(data)



                return summarizer_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            summarizer_type_1 = AssaysCreateJsonBodySummarizerType1.from_dict(data)



            return summarizer_type_1

        summarizer = _parse_summarizer(d.pop("summarizer"))


        alert_threshold = d.pop("alert_threshold")

        created_at = isoparse(d.pop("created_at"))




        workspace_id = d.pop("workspace_id")

        id = d.pop("id", UNSET)

        warning_threshold = d.pop("warning_threshold", UNSET)

        _last_window_start = d.pop("last_window_start", UNSET)
        last_window_start: Union[Unset, None, datetime.datetime]
        if _last_window_start is None:
            last_window_start = None
        elif isinstance(_last_window_start,  Unset):
            last_window_start = UNSET
        else:
            last_window_start = isoparse(_last_window_start)




        _run_until = d.pop("run_until", UNSET)
        run_until: Union[Unset, None, datetime.datetime]
        if _run_until is None:
            run_until = None
        elif isinstance(_run_until,  Unset):
            run_until = UNSET
        else:
            run_until = isoparse(_run_until)




        _last_run = d.pop("last_run", UNSET)
        last_run: Union[Unset, None, datetime.datetime]
        if _last_run is None:
            last_run = None
        elif isinstance(_last_run,  Unset):
            last_run = UNSET
        else:
            last_run = isoparse(_last_run)




        assays_create_json_body = cls(
            name=name,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            active=active,
            status=status,
            iopath=iopath,
            baseline=baseline,
            window=window,
            summarizer=summarizer,
            alert_threshold=alert_threshold,
            created_at=created_at,
            workspace_id=workspace_id,
            id=id,
            warning_threshold=warning_threshold,
            last_window_start=last_window_start,
            run_until=run_until,
            last_run=last_run,
        )

        assays_create_json_body.additional_properties = d
        return assays_create_json_body

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
