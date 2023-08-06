from typing import TYPE_CHECKING, cast, List
from .object import *

if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from .client import Client
    from .model import Model


import gql  # type: ignore
import yaml


class ModelConfig(Object):
    """Wraps a backend ModelConfig object."""

    def __init__(
        self, client: Optional["Client"], data: Dict[str, Any], standalone=False
    ) -> None:
        self.client = client
        super().__init__(
            gql_client=client._gql_client if client is not None else None,
            data=data,
            standalone=standalone,
        )

    @staticmethod
    def as_standalone(
        model: "Model",
        filter_threshold: Optional[float] = None,
        runtime: Optional[str] = None,
        tensor_fields: Optional[List[str]] = None,
    ) -> "ModelConfig":
        """Creates a ModelConfig intended for use in generating standalone configurations"""
        constructor_dict = {
            "id": -1,
            "model": model,
            "filter_threshold": filter_threshold,
            "runtime": runtime,
            "tensor_fields": tensor_fields,
        }
        return ModelConfig(None, data=constructor_dict, standalone=True)

    @property
    def inputs(self):
        return self.model().inputs

    @property
    def outputs(self):
        return self.model().outputs

    def to_yaml(self):
        """Generates a yaml file for standalone engines"""
        extra = {
            "model_id": self.model().name(),
            "model_version": self.model().version(),
        }
        return self._yaml(extra)

    def to_k8s_yaml(self):
        # XXX - the deployment manager currently stitches this together
        extra = {
            "name": self.model().name(),
            "version": self.model().version(),
            "sha": self.model().sha(),
        }
        return self._yaml(extra)

    def _yaml(self, yaml_dict):
        if self.filter_threshold():
            yaml_dict["filter_threshold"] = self.filter_threshold()
        if self.runtime():
            yaml_dict["runtime"] = self.runtime()
        if self.tensor_fields():
            yaml_dict["tensor_fields"] = self.tensor_fields()
        if type(self._input_schema) == str:
            yaml_dict["input_schema"] = self._input_schema
        if type(self._output_schema) == str:
            yaml_dict["output_schema"] = self._output_schema
        if type(self._batch_config) == str:
            yaml_dict["batch_config"] = self._batch_config
        return yaml.dump(yaml_dict)

    def _fill(self, data: Dict[str, Any]) -> None:
        """Fills an object given a response dictionary from the GraphQL API.

        Only the primary key member must be present; other members will be
        filled in via rehydration if their corresponding member function is
        called.
        """
        from .model import Model  # Avoids circular imports

        for required_attribute in ["id"]:
            if required_attribute not in data:
                raise RequiredAttributeMissing(
                    self.__class__.__name__, required_attribute
                )
        # Required
        self._id = data["id"]

        # Optional
        self._filter_threshold = value_if_present(data, "filter_threshold")
        self._model = (
            (
                data["model"]
                if isinstance(data["model"], Model)
                else Model(
                    client=self.client,
                    data=data["model"],
                    standalone=self._standalone,
                )
            )
            if "model" in data
            else DehydratedValue()
        )
        self._runtime = value_if_present(data, "runtime")
        self._tensor_fields = value_if_present(data, "tensor_fields")
        self._input_schema = value_if_present(data, "input_schema")
        self._output_schema = value_if_present(data, "output_schema")
        self._batch_config = value_if_present(data, "batch_config")

    def _fetch_attributes(self) -> Dict[str, Any]:
        """Fetches all member data from the GraphQL API."""
        assert self.client is not None
        return self.client._gql_client.execute(
            gql.gql(
                """
                query ModelConfigById($model_config_id: bigint!) {
                  model_config_by_pk(id: $model_config_id) {
                    id
                    filter_threshold
                    model {
                      id
                    }
                    runtime
                    tensor_fields
                  }
                }
            """
            ),
            variable_values={
                "model_config_id": self._id,
            },
        )["model_config_by_pk"]

    def id(self) -> int:
        return self._id

    @rehydrate("_filter_threshold")
    def filter_threshold(self) -> float:
        return cast(float, self._filter_threshold)

    @rehydrate("_model")
    def model(self) -> "Model":
        from .model import Model  # Avoids circular imports

        return cast(Model, self._model)

    @rehydrate("_runtime")
    def runtime(self) -> str:
        return cast(str, self._runtime)

    @rehydrate("_tensor_fields")
    def tensor_fields(self) -> List[str]:
        return cast(List[str], self._tensor_fields)
