from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.pipelines_copy_pipeline_json_body_engine_config import \
      PipelinesCopyPipelineJsonBodyEngineConfig





T = TypeVar("T", bound="PipelinesCopyPipelineJsonBody")


@attr.s(auto_attribs=True)
class PipelinesCopyPipelineJsonBody:
    """  Request to create a copy of a pipeline.

        Attributes:
            name (str):  Pipeline name.
            workspace_id (int):  Workspace identifier.
            source_pipeline (int):  Source pipeline identifier.
            deploy (Union[Unset, None, str]):  Optional deployment indicator.
            engine_config (Union[Unset, None, PipelinesCopyPipelineJsonBodyEngineConfig]):  Optional engine configuration to
                use.
            pipeline_version (Union[Unset, None, str]):  Optional pipeline version to create.
     """

    name: str
    workspace_id: int
    source_pipeline: int
    deploy: Union[Unset, None, str] = UNSET
    engine_config: Union[Unset, None, 'PipelinesCopyPipelineJsonBodyEngineConfig'] = UNSET
    pipeline_version: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        workspace_id = self.workspace_id
        source_pipeline = self.source_pipeline
        deploy = self.deploy
        engine_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_config, Unset):
            engine_config = self.engine_config.to_dict() if self.engine_config else None

        pipeline_version = self.pipeline_version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "workspace_id": workspace_id,
            "source_pipeline": source_pipeline,
        })
        if deploy is not UNSET:
            field_dict["deploy"] = deploy
        if engine_config is not UNSET:
            field_dict["engine_config"] = engine_config
        if pipeline_version is not UNSET:
            field_dict["pipeline_version"] = pipeline_version

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pipelines_copy_pipeline_json_body_engine_config import \
            PipelinesCopyPipelineJsonBodyEngineConfig
        d = src_dict.copy()
        name = d.pop("name")

        workspace_id = d.pop("workspace_id")

        source_pipeline = d.pop("source_pipeline")

        deploy = d.pop("deploy", UNSET)

        _engine_config = d.pop("engine_config", UNSET)
        engine_config: Union[Unset, None, PipelinesCopyPipelineJsonBodyEngineConfig]
        if _engine_config is None:
            engine_config = None
        elif isinstance(_engine_config,  Unset):
            engine_config = UNSET
        else:
            engine_config = PipelinesCopyPipelineJsonBodyEngineConfig.from_dict(_engine_config)




        pipeline_version = d.pop("pipeline_version", UNSET)

        pipelines_copy_pipeline_json_body = cls(
            name=name,
            workspace_id=workspace_id,
            source_pipeline=source_pipeline,
            deploy=deploy,
            engine_config=engine_config,
            pipeline_version=pipeline_version,
        )

        pipelines_copy_pipeline_json_body.additional_properties = d
        return pipelines_copy_pipeline_json_body

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
