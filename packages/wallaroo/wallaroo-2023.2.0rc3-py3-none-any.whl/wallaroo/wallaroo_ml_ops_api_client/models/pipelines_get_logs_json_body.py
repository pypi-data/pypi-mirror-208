from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.pipelines_get_logs_json_body_order import \
    PipelinesGetLogsJsonBodyOrder
from ..types import UNSET, Unset

T = TypeVar("T", bound="PipelinesGetLogsJsonBody")


@attr.s(auto_attribs=True)
class PipelinesGetLogsJsonBody:
    """  Request to retrieve inference logs for a pipeline.

        Attributes:
            pipeline_id (str):  Pipeline identifier.
            workspace_id (int):  Workspace identifier.
            order (PipelinesGetLogsJsonBodyOrder):  Iteration order
            cursor (Union[Unset, None, str]):  Cursor returned with a previous page of results
            page_size (Union[Unset, None, int]):  Max records per page
            start_time (Union[Unset, None, str]):  RFC 3339 start time
            end_time (Union[Unset, None, str]):  RFC 3339 end time
     """

    pipeline_id: str
    workspace_id: int
    order: PipelinesGetLogsJsonBodyOrder
    cursor: Union[Unset, None, str] = UNSET
    page_size: Union[Unset, None, int] = UNSET
    start_time: Union[Unset, None, str] = UNSET
    end_time: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_id = self.pipeline_id
        workspace_id = self.workspace_id
        order = self.order.value

        cursor = self.cursor
        page_size = self.page_size
        start_time = self.start_time
        end_time = self.end_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_id": pipeline_id,
            "workspace_id": workspace_id,
            "order": order,
        })
        if cursor is not UNSET:
            field_dict["cursor"] = cursor
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline_id = d.pop("pipeline_id")

        workspace_id = d.pop("workspace_id")

        order = PipelinesGetLogsJsonBodyOrder(d.pop("order"))




        cursor = d.pop("cursor", UNSET)

        page_size = d.pop("page_size", UNSET)

        start_time = d.pop("start_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        pipelines_get_logs_json_body = cls(
            pipeline_id=pipeline_id,
            workspace_id=workspace_id,
            order=order,
            cursor=cursor,
            page_size=page_size,
            start_time=start_time,
            end_time=end_time,
        )

        pipelines_get_logs_json_body.additional_properties = d
        return pipelines_get_logs_json_body

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
