import base64
import datetime
from typing import TYPE_CHECKING, List, Tuple, cast

import gql  # type: ignore
import pandas as pd
import pyarrow as pa  # type: ignore
import requests
from dateutil import parser as dateparse

from .checks import Variables, require_dns_compliance
from .deployment_config import DeploymentConfig, DeploymentConfigBuilder
from .object import *
from .utils import is_models_enabled
from .version import _user_agent
from .visibility import _Visibility

if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from .client import Client
    from .model_config import ModelConfig
    from .pipeline import Pipeline
    from .tag import Tag


# A little misleading, this is actually a ModelVersion or ModelVariant, associated with the `model` table, not the `models` table.
class Model(Object):
    """Wraps a backend Model object."""

    def __init__(
        self, client: Optional["Client"], data: Dict[str, Any], standalone=False
    ) -> None:
        self.client = client
        self._config: Optional["ModelConfig"] = None
        super().__init__(
            gql_client=client._gql_client if client is not None else None,
            data=data,
            standalone=standalone,
        )

    def __repr__(self) -> str:
        return str(
            {
                "name": self.name(),
                "version": self.version(),
                "file_name": self.file_name(),
                "image_path": self.image_path(),
                "last_update_time": self.last_update_time(),
            }
        )

    @staticmethod
    def as_standalone(name: str, version: str, file_name: str) -> "Model":
        """Creates a Model intended for use in generating standalone configurations"""
        constructor_dict = {
            "model_id": name,
            "model_version": version,
            "file_name": file_name,
            "id": -1,
        }
        return Model(None, constructor_dict, standalone=True)

    def _fill(self, data: Dict[str, Any]) -> None:
        """Fills an object given a response dictionary from the GraphQL API.

        Only the primary key member must be present; other members will be
        filled in via rehydration if their corresponding member function is
        called.
        """
        from .tag import Tag

        for required_attribute in ["id"]:
            if required_attribute not in data:
                raise RequiredAttributeMissing(
                    self.__class__.__name__, required_attribute
                )
        # Required
        self._id = data["id"]

        # Optional
        self._name = value_if_present(data, "model_id")
        self._version = value_if_present(data, "model_version")
        self._models_pk_id = value_if_present(data, "models_pk_id")
        self._sha = value_if_present(data, "sha")
        self._status = value_if_present(data, "status")
        self._file_name = value_if_present(data, "file_name")
        self._image_path = value_if_present(data, "image_path")
        self._last_update_time = (
            dateparse.isoparse(data["updated_at"])
            if "updated_at" in data
            else DehydratedValue()
        )
        self._visibility = (
            _Visibility.from_str(data["visibility"])
            if "visibility" in data
            else DehydratedValue()
        )
        self._tags = (
            [Tag(self.client, tag["tag"]) for tag in data["model_tags"]]
            if "model_tags" in data
            else DehydratedValue()
        )

    def _fetch_attributes(self) -> Dict[str, Any]:
        """Fetches all member data from the GraphQL API."""
        return self._gql_client.execute(
            gql.gql(
                f"""
            query ModelById {{
                model_by_pk(id: {self._id}) {{
                    id
                    model_id
                    model_version
                    models_pk_id    
                    sha
                    status
                    file_name
                    image_path
                    updated_at
                    visibility
                    model_tags {{
                      tag {{
                        id
                        tag
                      }}
                    }}
                }}
            }}
            """
            )
        )["model_by_pk"]

    def id(self) -> int:
        return self._id

    def uid(self) -> str:
        return f"{self.name()}-{self.id()}"

    @rehydrate("_name")
    def name(self) -> str:
        return cast(str, self._name)

    @rehydrate("_version")
    def version(self) -> str:
        return cast(str, self._version)

    # TODO: Find other models by finding the parent?
    # @rehydrate("_versions")
    # def versions(self) -> "Models":
    #     from .models import Models

    #     return Models(client=self.client, data={"id": self._models_pk_id})

    @rehydrate("_models_pk_id")
    def models_pk_id(self) -> str:
        return cast(str, self._models_pk_id)

    @rehydrate("_sha")
    def sha(self) -> str:
        return cast(str, self._sha)

    @rehydrate("_status")
    def status(self) -> str:
        return cast(str, self._status)

    @rehydrate("_file_name")
    def file_name(self) -> str:
        return cast(str, self._file_name)

    @rehydrate("_image_path")
    def image_path(self) -> str:
        return cast(str, self._image_path)

    @rehydrate("_last_update_time")
    def last_update_time(self) -> datetime.datetime:
        return cast(datetime.datetime, self._last_update_time)

    @property
    def inputs(self):
        return Variables(self.name(), "input")

    @property
    def outputs(self):
        return Variables(self.name(), "output")

    @rehydrate("_tags")
    def tags(self) -> List["Tag"]:
        from .tag import Tag  # avoids import cycles

        return cast(List[Tag], self._tags)

    @rehydrate("_config")
    def rehydrate_config(self) -> "ModelConfig":
        from .model_config import ModelConfig

        if self._config is not None:
            return self._config
        if self.client is None:
            raise Exception("Cannot retrieve current model config, client is None.")
        assert self.client is not None
        base = self.client.api_endpoint + f"/v1/api/models/get_config_by_id"
        headers = {"User-Agent": _user_agent}

        raw = requests.post(
            base,
            auth=self.client.auth,
            headers=headers,
            json={"model_id": self.id()},
        )
        if raw.status_code > 299:
            raise Exception(
                "Failed to retrieve config from api, and failed to automatically configure model."
            )
        possible_model_config = raw.json()
        if possible_model_config["model_config"]:
            return ModelConfig(
                client=self.client, data=possible_model_config["model_config"]
            )
        else:
            raise Exception(
                "Failed to determine model configuration, could not auto configure based on name, and no existing "
                "model configuration was present. "
            )

    def _update_visibility(self, visibility: _Visibility):
        assert self.client is not None
        return self._fill(
            self.client._gql_client.execute(
                gql.gql(
                    """
                mutation UpdateModelVisibility(
                    $model_pk: bigint!,
                    $visibility: String
                ) {
                  update_model(where: {id: {_eq: $model_pk}}, _set: {visibility: $visibility}) {
                        returning {
                          id
                          model_id
                          model_version
                          file_name
                          visibility
                          updated_at
                        }
                    }
                }
                """
                ),
                variable_values={
                    "model_pk": self._id,
                    "visibility": visibility,
                },
            )["update_model"]["returning"][0]
        )

    def config(self) -> "ModelConfig":
        if self._config is None:
            try:
                self.configure()
            except Exception:
                self._config = self.rehydrate_config()
        assert self._config is not None
        return cast("ModelConfig", self._config)

    def configure(
        self,
        runtime: Optional[str] = None,
        tensor_fields: List[str] = None,
        filter_threshold: float = None,
        input_schema: Optional[pa.Schema] = None,
        output_schema: Optional[pa.Schema] = None,
        batch_config: Optional[str] = None,
    ) -> "Model":
        if is_models_enabled():
            return self._configure_via_models(
                tensor_fields,
                filter_threshold,
                input_schema,
                output_schema,
                batch_config,
            )
        else:
            return self._configure_via_gql(
                runtime,
                tensor_fields,
                filter_threshold,
                input_schema,
                output_schema,
                batch_config,
            )

    def _configure_via_gql(
        self,
        runtime: Optional[str] = None,
        tensor_fields: List[str] = None,
        filter_threshold: float = None,
        input_schema: Optional[pa.Schema] = None,
        output_schema: Optional[pa.Schema] = None,
        batch_config: Optional[str] = None,
    ) -> "Model":
        from .model_config import ModelConfig  # Avoids circular imports

        if runtime is None:
            filename_to_runtime = {".onnx": "onnx", ".py": "python"}

            runtimes = [
                v
                for (k, v) in filename_to_runtime.items()
                if self.file_name().endswith(k)
            ]
            if not runtimes:
                raise DeploymentError(
                    f"runtime cannot be inferred from filename: {self.file_name()}"
                )
            if len(runtimes) > 1:
                raise DeploymentError(
                    f"Multiple runtimes possible for filename {self.file_name()}: {runtimes}"
                )
            runtime = runtimes[0]

        if tensor_fields:
            if not isinstance(tensor_fields, List) or not all(
                isinstance(s, str) for s in tensor_fields
            ):
                raise DeploymentError(
                    f"tensor_fields must be a list of strings, received: {tensor_fields}"
                )

        if input_schema:
            input_schema = base64.b64encode(bytes(input_schema.serialize())).decode(
                "utf8"
            )
        elif runtime == "mlflow":
            raise DeploymentError("input_schema is required for mlflow models")

        if output_schema:
            output_schema = base64.b64encode(bytes(output_schema.serialize())).decode(
                "utf8"
            )
        elif runtime == "mlflow":
            raise DeploymentError("output_schema is required for mlflow models")

        q = gql.gql(
            """
            mutation ConfigureModel($model_id: bigint!, $runtime: String, $tensor_fields: jsonb, $filter_threshold: float8, $input_schema: String, $output_schema: String, $batch_config: String) {
                insert_model_config(objects: {filter_threshold: $filter_threshold, model_id: $model_id, runtime: $runtime, tensor_fields: $tensor_fields, input_schema: $input_schema, output_schema: $output_schema, batch_config: $batch_config}) {
                returning {
                    id
                    model_id
                    runtime
                    tensor_fields
                    filter_threshold
                    input_schema
                    output_schema
                    batch_config
                    model {
                        id
                    }
                }
            }
            }
            """
        )
        variables = {
            "model_id": self.id(),
            "runtime": runtime,
            "tensor_fields": tensor_fields,
            "filter_threshold": filter_threshold,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "batch_config": batch_config,
        }
        assert self.client is not None
        data = self.client._gql_client.execute(q, variable_values=variables)

        self._config = ModelConfig(
            client=self.client,
            data=data["insert_model_config"]["returning"][0],
        )
        self._config._model = self
        return self

    def _configure_via_models(
        self,
        tensor_fields: List[str] = None,
        filter_threshold: float = None,
        input_schema: Optional[pa.Schema] = None,
        output_schema: Optional[pa.Schema] = None,
        batch_config: Optional[str] = None,
    ) -> "Model":
        from .model_config import ModelConfig  # Avoids circular imports

        request: Dict[str, Any] = {"model_version_id": self.id()}

        if tensor_fields:
            request["tensor_fields"] = tensor_fields
        if filter_threshold:
            request["filter_threshold"] = filter_threshold
        if input_schema:
            request["input_schema"] = base64.b64encode(
                bytes(input_schema.serialize())
            ).decode("utf8")
        if output_schema:
            request["output_schema"] = base64.b64encode(
                bytes(output_schema.serialize())
            ).decode("utf8")
        if batch_config:
            request["batch_config"] = batch_config

        assert self.client is not None
        base = self.client.api_endpoint + f"/v1/api/models/insert_model_config"
        headers = {"User-Agent": _user_agent}

        try:
            raw = requests.post(
                base,
                auth=self.client.auth,
                headers=headers,
                json=request,
            )
            raw.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise requests.exceptions.HTTPError(
                f"Failed to insert model config: {http_error.response.text}"
            ) from http_error

        possible_model_config = raw.json()
        if possible_model_config["model_config"]:
            self._config = ModelConfig(
                client=self.client,
                data=possible_model_config["model_config"],
            )
            self._config._model = self
            return self
        else:
            raise Exception(
                "Failed to determine model configuration, could not auto configure based on name, and no existing "
                "model configuration was present. "
            )

    def logs(
        self,
        limit: int = 100,
        valid: Optional[bool] = None,
        arrow: Optional[bool] = False,
    ) -> Tuple[Any, Union[str, None]]:
        topic = f"model-{self.name()}-inference"
        if valid is False:
            topic += "-failures"
        assert self.client is not None
        logs = self.client.get_logs(topic, limit, arrow=arrow)
        return logs if isinstance(logs, (pa.Table, pd.DataFrame)) else logs[0]

    def deploy(
        self,
        pipeline_name: str,
        deployment_config: Optional[DeploymentConfig] = None,
    ) -> "Pipeline":
        """Convenience function to quickly deploy a Model. It will configure the model,
        create a pipeline with a single model step, deploy it, and return the pipeline.

        Typically, the configure() method is used to configure a model prior to
        deploying it. However, if a default configuration is sufficient, this
        function can be used to quickly deploy with said default configuration.

        The filename this Model was generated from needs to have a recognizable
        file extension so that the runtime can be inferred. Currently, this is:

        * `.onnx` -> ONNX runtime

        :param str deployment_name: Name of the deployment to create. Must be
            unique across all deployments. Deployment names must be ASCII alpha-numeric
            characters plus dash (-) only.

        """

        assert self.client is not None

        require_dns_compliance(pipeline_name)

        workspace_id = (
            None if self.client is None else self.client.get_current_workspace().id()
        )

        if deployment_config is None:
            deployment_config = DeploymentConfigBuilder(
                workspace_id=workspace_id
            ).build()
        else:
            deployment_config.guarantee_workspace_id(workspace_id=workspace_id)

        pipeline = self.client.build_pipeline(pipeline_name)

        pipeline.add_model_step(self)

        pipeline.deploy(pipeline_name, deployment_config=deployment_config)

        return pipeline

        # TODO - wait_for_running


class ModelVersions(List[Model]):
    """Wraps a list of Models for display in a display-aware environment like Jupyter."""

    def _repr_html_(self) -> str:
        def row(model: Model):
            return f"""
            <tr>
                <td>{model.name()}</td>
                <td>{model.version()}</td>
                <td>{model.file_name()}</td>
                <td>{model.image_path()}</td>
                <td>{model.last_update_time()}</td>
            </tr>
          """

        fields = ["name", "version", "file_name", "image_path", "last_update_time"]
        if not self:
            return "(no model versions)"
        else:
            return (
                "<table>"
                + "<tr><th>"
                + "</th><th>".join(fields)
                + "</th></tr>"
                + ("".join([row(m) for m in self]))
                + "</table>"
            )
