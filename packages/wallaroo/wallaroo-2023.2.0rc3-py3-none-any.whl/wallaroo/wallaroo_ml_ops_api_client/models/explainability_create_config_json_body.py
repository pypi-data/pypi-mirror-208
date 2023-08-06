from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.explainability_create_config_json_body_feature_bounds import \
      ExplainabilityCreateConfigJsonBodyFeatureBounds





T = TypeVar("T", bound="ExplainabilityCreateConfigJsonBody")


@attr.s(auto_attribs=True)
class ExplainabilityCreateConfigJsonBody:
    """  A configuration for reference and adhoc explainability requests

        Attributes:
            workspace_id (int):  The users workspace
            reference_pipeline_version (str):  The production pipeline to be analyzed
            id (Union[Unset, None, str]):
            explainability_pipeline_version (Union[Unset, None, str]):  The copy of the production pipeline that will be
                used for analysis.
            num_points (Union[Unset, None, int]):  How many points to sample for each feature bounds range
            feature_names (Union[Unset, None, List[str]]):  Names of features for improved reporting.
            feature_bounds (Union[Unset, None, ExplainabilityCreateConfigJsonBodyFeatureBounds]):  Calculated feature bounds
            output_names (Union[Unset, None, List[str]]):  The names of the outputs for improved reporting
     """

    workspace_id: int
    reference_pipeline_version: str
    id: Union[Unset, None, str] = UNSET
    explainability_pipeline_version: Union[Unset, None, str] = UNSET
    num_points: Union[Unset, None, int] = UNSET
    feature_names: Union[Unset, None, List[str]] = UNSET
    feature_bounds: Union[Unset, None, 'ExplainabilityCreateConfigJsonBodyFeatureBounds'] = UNSET
    output_names: Union[Unset, None, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        reference_pipeline_version = self.reference_pipeline_version
        id = self.id
        explainability_pipeline_version = self.explainability_pipeline_version
        num_points = self.num_points
        feature_names: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.feature_names, Unset):
            if self.feature_names is None:
                feature_names = None
            else:
                feature_names = self.feature_names




        feature_bounds: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.feature_bounds, Unset):
            feature_bounds = self.feature_bounds.to_dict() if self.feature_bounds else None

        output_names: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.output_names, Unset):
            if self.output_names is None:
                output_names = None
            else:
                output_names = self.output_names





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_id": workspace_id,
            "reference_pipeline_version": reference_pipeline_version,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if explainability_pipeline_version is not UNSET:
            field_dict["explainability_pipeline_version"] = explainability_pipeline_version
        if num_points is not UNSET:
            field_dict["num_points"] = num_points
        if feature_names is not UNSET:
            field_dict["feature_names"] = feature_names
        if feature_bounds is not UNSET:
            field_dict["feature_bounds"] = feature_bounds
        if output_names is not UNSET:
            field_dict["output_names"] = output_names

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.explainability_create_config_json_body_feature_bounds import \
            ExplainabilityCreateConfigJsonBodyFeatureBounds
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        reference_pipeline_version = d.pop("reference_pipeline_version")

        id = d.pop("id", UNSET)

        explainability_pipeline_version = d.pop("explainability_pipeline_version", UNSET)

        num_points = d.pop("num_points", UNSET)

        feature_names = cast(List[str], d.pop("feature_names", UNSET))


        _feature_bounds = d.pop("feature_bounds", UNSET)
        feature_bounds: Union[Unset, None, ExplainabilityCreateConfigJsonBodyFeatureBounds]
        if _feature_bounds is None:
            feature_bounds = None
        elif isinstance(_feature_bounds,  Unset):
            feature_bounds = UNSET
        else:
            feature_bounds = ExplainabilityCreateConfigJsonBodyFeatureBounds.from_dict(_feature_bounds)




        output_names = cast(List[str], d.pop("output_names", UNSET))


        explainability_create_config_json_body = cls(
            workspace_id=workspace_id,
            reference_pipeline_version=reference_pipeline_version,
            id=id,
            explainability_pipeline_version=explainability_pipeline_version,
            num_points=num_points,
            feature_names=feature_names,
            feature_bounds=feature_bounds,
            output_names=output_names,
        )

        explainability_create_config_json_body.additional_properties = d
        return explainability_create_config_json_body

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
