from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.assays_filter_json_body_sort_by import AssaysFilterJsonBodySortBy
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.assays_filter_json_body_drift_window import \
      AssaysFilterJsonBodyDriftWindow





T = TypeVar("T", bound="AssaysFilterJsonBody")


@attr.s(auto_attribs=True)
class AssaysFilterJsonBody:
    """ 
        Attributes:
            workspace_id (int):
            pipeline_id (int):
            sort_by (AssaysFilterJsonBodySortBy):
            name (Union[Unset, None, str]):
            active (Union[Unset, None, bool]):
            drift_window (Union[Unset, None, AssaysFilterJsonBodyDriftWindow]):
     """

    workspace_id: int
    pipeline_id: int
    sort_by: AssaysFilterJsonBodySortBy
    name: Union[Unset, None, str] = UNSET
    active: Union[Unset, None, bool] = UNSET
    drift_window: Union[Unset, None, 'AssaysFilterJsonBodyDriftWindow'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        pipeline_id = self.pipeline_id
        sort_by = self.sort_by.value

        name = self.name
        active = self.active
        drift_window: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.drift_window, Unset):
            drift_window = self.drift_window.to_dict() if self.drift_window else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_id": workspace_id,
            "pipeline_id": pipeline_id,
            "sort_by": sort_by,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if active is not UNSET:
            field_dict["active"] = active
        if drift_window is not UNSET:
            field_dict["drift_window"] = drift_window

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_filter_json_body_drift_window import \
            AssaysFilterJsonBodyDriftWindow
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        pipeline_id = d.pop("pipeline_id")

        sort_by = AssaysFilterJsonBodySortBy(d.pop("sort_by"))




        name = d.pop("name", UNSET)

        active = d.pop("active", UNSET)

        _drift_window = d.pop("drift_window", UNSET)
        drift_window: Union[Unset, None, AssaysFilterJsonBodyDriftWindow]
        if _drift_window is None:
            drift_window = None
        elif isinstance(_drift_window,  Unset):
            drift_window = UNSET
        else:
            drift_window = AssaysFilterJsonBodyDriftWindow.from_dict(_drift_window)




        assays_filter_json_body = cls(
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
            sort_by=sort_by,
            name=name,
            active=active,
            drift_window=drift_window,
        )

        assays_filter_json_body.additional_properties = d
        return assays_filter_json_body

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
