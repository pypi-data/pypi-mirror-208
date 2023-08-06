from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.assays_get_baseline_json_body_next import \
      AssaysGetBaselineJsonBodyNext





T = TypeVar("T", bound="AssaysGetBaselineJsonBody")


@attr.s(auto_attribs=True)
class AssaysGetBaselineJsonBody:
    """  Request to retrieve an assay baseline.

        Attributes:
            pipeline_name (str):  Pipeline name.
            workspace_id (Union[Unset, None, int]):  Workspace identifier.
            start (Union[Unset, None, str]):  Start date and time.
            end (Union[Unset, None, str]):  End date and time.
            model_name (Union[Unset, None, str]):  Model name.
            limit (Union[Unset, None, int]):  Maximum number of baselines to return.
            next_ (Union[Unset, None, AssaysGetBaselineJsonBodyNext]):  Pagination object. Returned as part of previous
                requests.
     """

    pipeline_name: str
    workspace_id: Union[Unset, None, int] = UNSET
    start: Union[Unset, None, str] = UNSET
    end: Union[Unset, None, str] = UNSET
    model_name: Union[Unset, None, str] = UNSET
    limit: Union[Unset, None, int] = UNSET
    next_: Union[Unset, None, 'AssaysGetBaselineJsonBodyNext'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        pipeline_name = self.pipeline_name
        workspace_id = self.workspace_id
        start = self.start
        end = self.end
        model_name = self.model_name
        limit = self.limit
        next_: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.next_, Unset):
            next_ = self.next_.to_dict() if self.next_ else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pipeline_name": pipeline_name,
        })
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if limit is not UNSET:
            field_dict["limit"] = limit
        if next_ is not UNSET:
            field_dict["next"] = next_

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_get_baseline_json_body_next import \
            AssaysGetBaselineJsonBodyNext
        d = src_dict.copy()
        pipeline_name = d.pop("pipeline_name")

        workspace_id = d.pop("workspace_id", UNSET)

        start = d.pop("start", UNSET)

        end = d.pop("end", UNSET)

        model_name = d.pop("model_name", UNSET)

        limit = d.pop("limit", UNSET)

        _next_ = d.pop("next", UNSET)
        next_: Union[Unset, None, AssaysGetBaselineJsonBodyNext]
        if _next_ is None:
            next_ = None
        elif isinstance(_next_,  Unset):
            next_ = UNSET
        else:
            next_ = AssaysGetBaselineJsonBodyNext.from_dict(_next_)




        assays_get_baseline_json_body = cls(
            pipeline_name=pipeline_name,
            workspace_id=workspace_id,
            start=start,
            end=end,
            model_name=model_name,
            limit=limit,
            next_=next_,
        )

        assays_get_baseline_json_body.additional_properties = d
        return assays_get_baseline_json_body

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
