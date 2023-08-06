from typing import TYPE_CHECKING, cast, Optional, Dict
from .object import *

import gql  # type: ignore
import json
import yaml


class EngineConfig:
    """Wraps an engine config."""

    # NOTE: refer to /conductor/helm/payloads/deployment-manager/helm/default-values and
    # /conductor/helm/payloads/deployment-manager/helm/orchestra-deployment.yaml
    # for reasonable defaults
    def __init__(
        self,
        cpus: int,
        inference_channel_size: Optional[int] = None,
        model_concurrency: Optional[int] = None,
        pipeline_config_directory: Optional[str] = None,
        model_config_directory: Optional[str] = None,
        model_directory: Optional[str] = None,
        audit_logging: bool = False,
        standalone: bool = False,
    ) -> None:
        self._cpus = cpus
        self._inference_channel_size = (
            inference_channel_size if inference_channel_size else 10000
        )
        self._model_concurrency = model_concurrency if model_concurrency else 2
        self._audit_logging = audit_logging
        self._pipeline_config_directory = pipeline_config_directory
        self._model_config_directory = model_config_directory
        self._model_directory = model_directory
        self._standalone = standalone

    @staticmethod
    def as_standalone(
        cpus: int,
        inference_channel_size: Optional[int] = None,
        model_concurrency: Optional[int] = None,
        pipeline_config_directory: Optional[str] = None,
        model_config_directory: Optional[str] = None,
        model_directory: Optional[str] = None,
    ) -> "EngineConfig":
        """Creates an EngineConfig for use with standalone mode"""
        return EngineConfig(
            cpus,
            inference_channel_size=inference_channel_size,
            model_concurrency=model_concurrency,
            pipeline_config_directory=pipeline_config_directory,
            model_config_directory=model_config_directory,
            model_directory=model_directory,
            audit_logging=False,
            standalone=True,
        )

    # TODO: Is there a better way to keep this in sync with our helm chart?
    def _to_dict(self) -> Dict[str, Any]:
        """Generate a dictionary representation for use to coversion to json or yaml"""
        config: Dict[str, Any] = {
            "cpus": self._cpus,
        }
        if self._inference_channel_size:
            config["inference_channel_size"] = self._inference_channel_size
        if self._model_concurrency:
            config["model_server"] = {"model_concurrency": self._model_concurrency}
        config["audit_logging"] = {"enabled": self._audit_logging}
        if self._standalone:
            if "model_server" in config:
                config["model_server"]["model_dir"] = "/models"
            config["input_type"] = "json"
            config["input_protocol"] = "http"
            config["onnx"] = {"intra_op_parallelism_threads": self._cpus}
            config["k8s"] = {"namespace": "wallaroo-standalone"}
            config["sink"] = {"type": "http_response"}
            config["directories"] = {
                "model_config": (
                    self._model_config_directory
                    if self._model_config_directory
                    else "/modelconfig"
                ),
                "pipeline_config": (
                    self._pipeline_config_directory
                    if self._pipeline_config_directory
                    else "/pipelineconfig"
                ),
                "model": (self._model_directory if self._model_directory else "/model"),
            }
        return config

    def to_json(self) -> str:
        """Returns a json representation of this object"""
        return json.dumps(self._to_dict())

    def to_yaml(self) -> str:
        """Returns a yaml representation of this object for use with standalone mode"""
        return yaml.dump(self._to_dict())
