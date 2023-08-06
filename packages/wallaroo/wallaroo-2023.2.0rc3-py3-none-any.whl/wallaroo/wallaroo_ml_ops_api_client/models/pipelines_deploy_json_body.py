from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.pipelines_deploy_json_body_engine_config import \
      PipelinesDeployJsonBodyEngineConfig
  from ..models.pipelines_deploy_json_body_models_item import \
      PipelinesDeployJsonBodyModelsItem





T = TypeVar("T", bound="PipelinesDeployJsonBody")


@attr.s(auto_attribs=True)
class PipelinesDeployJsonBody:
    """  Pipeline deployment request.

        Attributes:
            deploy_id (str):  Deployment identifier.
            pipeline_version_pk_id (int):  Internal pipeline version identifier.
            pipeline_id (int):  Pipeline identifier.
            engine_config (Union[Unset, None, PipelinesDeployJsonBodyEngineConfig]):  Optional engine configuration.
            model_configs (Union[Unset, None, List[int]]):  Optional model configurations.
            model_ids (Union[Unset, None, List[int]]):  Optional model identifiers.  If model_ids are passed in, we will
                create model_configs for them.
            models (Union[Unset, None, List['PipelinesDeployJsonBodyModelsItem']]):  Optional model.  Because model_ids may
                not be readily available for existing pipelines, they can pass in all the data again.
     """

    deploy_id: str
    pipeline_version_pk_id: int
    pipeline_id: int
    engine_config: Union[Unset, None, 'PipelinesDeployJsonBodyEngineConfig'] = UNSET
    model_configs: Union[Unset, None, List[int]] = UNSET
    model_ids: Union[Unset, None, List[int]] = UNSET
    models: Union[Unset, None, List['PipelinesDeployJsonBodyModelsItem']] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        deploy_id = self.deploy_id
        pipeline_version_pk_id = self.pipeline_version_pk_id
        pipeline_id = self.pipeline_id
        engine_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.engine_config, Unset):
            engine_config = self.engine_config.to_dict() if self.engine_config else None

        model_configs: Union[Unset, None, List[int]] = UNSET
        if not isinstance(self.model_configs, Unset):
            if self.model_configs is None:
                model_configs = None
            else:
                model_configs = self.model_configs




        model_ids: Union[Unset, None, List[int]] = UNSET
        if not isinstance(self.model_ids, Unset):
            if self.model_ids is None:
                model_ids = None
            else:
                model_ids = self.model_ids




        models: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.models, Unset):
            if self.models is None:
                models = None
            else:
                models = []
                for models_item_data in self.models:
                    models_item = models_item_data.to_dict()

                    models.append(models_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "deploy_id": deploy_id,
            "pipeline_version_pk_id": pipeline_version_pk_id,
            "pipeline_id": pipeline_id,
        })
        if engine_config is not UNSET:
            field_dict["engine_config"] = engine_config
        if model_configs is not UNSET:
            field_dict["model_configs"] = model_configs
        if model_ids is not UNSET:
            field_dict["model_ids"] = model_ids
        if models is not UNSET:
            field_dict["models"] = models

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pipelines_deploy_json_body_engine_config import \
            PipelinesDeployJsonBodyEngineConfig
        from ..models.pipelines_deploy_json_body_models_item import \
            PipelinesDeployJsonBodyModelsItem
        d = src_dict.copy()
        deploy_id = d.pop("deploy_id")

        pipeline_version_pk_id = d.pop("pipeline_version_pk_id")

        pipeline_id = d.pop("pipeline_id")

        _engine_config = d.pop("engine_config", UNSET)
        engine_config: Union[Unset, None, PipelinesDeployJsonBodyEngineConfig]
        if _engine_config is None:
            engine_config = None
        elif isinstance(_engine_config,  Unset):
            engine_config = UNSET
        else:
            engine_config = PipelinesDeployJsonBodyEngineConfig.from_dict(_engine_config)




        model_configs = cast(List[int], d.pop("model_configs", UNSET))


        model_ids = cast(List[int], d.pop("model_ids", UNSET))


        models = []
        _models = d.pop("models", UNSET)
        for models_item_data in (_models or []):
            models_item = PipelinesDeployJsonBodyModelsItem.from_dict(models_item_data)



            models.append(models_item)


        pipelines_deploy_json_body = cls(
            deploy_id=deploy_id,
            pipeline_version_pk_id=pipeline_version_pk_id,
            pipeline_id=pipeline_id,
            engine_config=engine_config,
            model_configs=model_configs,
            model_ids=model_ids,
            models=models,
        )

        pipelines_deploy_json_body.additional_properties = d
        return pipelines_deploy_json_body

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
