import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from dateutil import parser as dateparse

from wallaroo import queries

from .deployment import Deployment
from .deployment_config import DeploymentConfig, DeploymentConfigBuilder
from .model_config import ModelConfig
from .object import *
from .wallaroo_ml_ops_api_client.api.pipeline import pipelines_deploy
from .wallaroo_ml_ops_api_client.models import (
    pipelines_deploy_json_body,
    pipelines_deploy_json_body_engine_config,
)
from .wallaroo_ml_ops_api_client.models.pipelines_deploy_response_500 import (
    PipelinesDeployResponse500,
)
from .wallaroo_ml_ops_api_client.types import UNSET

if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from .client import Client
    from .pipeline import Pipeline


class PipelineVariant(Object):
    def __init__(self, client: Optional["Client"], data: Dict[str, Any]) -> None:
        self.client = client
        assert client is not None
        super().__init__(gql_client=client._gql_client, data=data)

    def _fill(self, data: Dict[str, Any]) -> None:
        from .pipeline import Pipeline  # avoids circular imports

        for required_attribute in ["id"]:
            if required_attribute not in data:
                raise RequiredAttributeMissing(
                    self.__class__.__name__, required_attribute
                )
        self._id = data["id"]

        self._create_time = (
            dateparse.isoparse(data["created_at"])
            if "created_at" in data
            else DehydratedValue()
        )
        self._last_update_time = (
            dateparse.isoparse(data["updated_at"])
            if "updated_at" in data
            else DehydratedValue()
        )
        self._name = value_if_present(data, "version")
        self._definition = value_if_present(data, "definition")
        self._pipeline = (
            Pipeline(client=self.client, data=data["pipeline"])
            if "pipeline" in data
            else DehydratedValue()
        )
        self._deployments = (
            [
                Deployment(
                    client=self.client,
                    data=elem["deployment"],
                )
                for elem in data["deployment_pipeline_versions"]
            ]
            if "deployment_pipeline_versions" in data
            else DehydratedValue()
        )
        self._model_configs = (
            [
                ModelConfig(
                    client=self.client,
                    data=elem["model_config"],
                )
                for elem in data["deployment_model_configs"]
            ]
            if "deployment_model_configs" in data
            else DehydratedValue()
        )

    def _fetch_attributes(self) -> Dict[str, Any]:
        return self._gql_client.execute(
            gql.gql(queries.named("PipelineVariantById")),
            variable_values={
                "variant_id": self._id,
            },
        )["pipeline_version_by_pk"]

    def id(self) -> int:
        return self._id

    @rehydrate("_create_time")
    def create_time(self) -> datetime.datetime:
        return cast(datetime.datetime, self._create_time)

    @rehydrate("_last_update_time")
    def last_update_time(self) -> datetime.datetime:
        return cast(datetime.datetime, self._last_update_time)

    @rehydrate("_name")
    def name(self) -> str:
        return cast(str, self._name)

    @rehydrate("_definition")
    def definition(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._definition)

    @rehydrate("_pipeline")
    def pipeline(self) -> "Pipeline":
        from .pipeline import Pipeline

        return cast(Pipeline, self._pipeline)

    @rehydrate("_deployments")
    def deployments(self) -> List[Deployment]:
        return cast(List[Deployment], self._deployments)

    @rehydrate("_model_configs")
    def model_configs(self) -> List[ModelConfig]:
        return cast(List[ModelConfig], self._model_configs)

    def deploy(
        self,
        deployment_name: str,
        model_configs: List[ModelConfig],
        config: Optional[DeploymentConfig] = None,
    ) -> Deployment:
        """Deploys this PipelineVariant.

        :param str deployment_name: Name of the new Deployment. Must be unique
            across all deployments.
        :param List[ModelConfig] model_configs: List of the configured models to
        use. These must be the same ModelConfigs used when creating the
            Pipeline.
        :param Optional[DeploymentConfig] config: Deployment configuration to use.
        :return: A Deployment object for the resulting deployment.
        :rtype: Deployment
        """
        workspace_id = (
            None if self.client is None else self.client.get_current_workspace().id()
        )
        if config is None:
            config = DeploymentConfigBuilder(workspace_id=workspace_id).build()
        else:
            config.guarantee_workspace_id(workspace_id=workspace_id)

        assert self.client is not None

        engine = pipelines_deploy_json_body_engine_config.PipelinesDeployJsonBodyEngineConfig.from_dict(
            config
        )
        model_config_ids = [mc.id() for mc in model_configs]
        body = pipelines_deploy_json_body.PipelinesDeployJsonBody(
            deployment_name,
            self.id(),
            self.pipeline().id(),
            engine,
            model_config_ids,
            UNSET,
            UNSET,
        )

        data = pipelines_deploy.sync(client=self.client.mlops(), json_body=body)
        if isinstance(data, PipelinesDeployResponse500):
            raise Exception(data.msg)

        if data is None:
            raise Exception("Failed to deploy.")

        deployment = Deployment(client=self.client, data=data.to_dict())

        deployment._rehydrate()

        # Increase timeout for each MLFlow image, up to a limit. Based on very limited testing,
        # multiple MLFlow images do require more time than a single image due to some network
        # saturation.
        timeout_multiplier = 1
        for mc in model_configs:
            if mc.runtime() == "mlflow" and timeout_multiplier < 3:
                timeout_multiplier += 1

        return deployment.wait_for_running(self.client.timeout * timeout_multiplier)


class PipelineVariants(List[PipelineVariant]):
    """Wraps a list of pipelines for display in a display-aware environment like Jupyter."""

    def _repr_html_(self) -> str:
        def row(pipeline_variant):
            # TODO: we shouldn't be accessing a protected member. No side effects now, so deal with it later.
            fmt = pipeline_variant.client._time_format
            pipeline = pipeline_variant.pipeline()
            tags = ", ".join([tag.tag() for tag in pipeline.tags()])
            deployments = pipeline_variant.deployments()
            deployed = (
                "(unknown)"
                if not deployments
                else pipeline_variant.deployments()[0].deployed()
            )
            model_configs = pipeline_variant.model_configs()
            steps = ", ".join([mc.model().name() for mc in model_configs])
            return (
                "<tr>"
                + f"<td>{pipeline.name()}</td>"
                + f"<td>{pipeline_variant.name()}</td>"
                + f"<td>{pipeline_variant.create_time().strftime(fmt)}</td>"
                + f"<td>{pipeline_variant.last_update_time().strftime(fmt)}</td>"
                + f"<td>{deployed}</td>"
                + f"<td>{tags}</td>"
                + f"<td>{steps}</td>"
                + "</tr>"
            )

        fields = [
            "name",
            "version",
            "creation_time",
            "last_updated_time",
            "deployed",
            "tags",
            "steps",
        ]

        if not self:
            return "(no pipelines)"
        else:
            return (
                "<table>"
                + "<tr><th>"
                + "</th><th>".join(fields)
                + "</th></tr>"
                + ("".join([row(p) for p in self]))
                + "</table>"
            )
