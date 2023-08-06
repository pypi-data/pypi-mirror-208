from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union
import json, os

if TYPE_CHECKING:
    from .model import Model


class DeploymentConfig(Dict):
    def guarantee_workspace_id(self, workspace_id: Optional[int]) -> "DeploymentConfig":
        if workspace_id is None:
            return self
        if self.get("workspace_id", None) is None:
            self["workspace_id"] = workspace_id
        return self


class DeploymentConfigBuilder(object):
    def __init__(self, workspace_id: Optional[int] = None) -> None:
        self._config: Dict[str, Any] = {
            "engine": {},
            "enginelb": {},
            "engineAux": {"images": {}},
            **({"workspace_id": workspace_id} if workspace_id is not None else {}),
        }

        env_config = os.environ.get("DEPLOYMENT_CONFIG", None)

        if env_config:
            conf = json.loads(env_config)
            setters: Dict[str, Callable[[Any], Any]] = {
                "image": self.image,
                "replicas": self.replica_count,
                "autoscale": self._autoscale,
                "cpus": self.cpus,
                "memory": self.memory,
                "lb_cpus": self.lb_cpus,
                "lb_memory": self.lb_memory,
            }
            for key, set in setters.items():
                if key in conf:
                    set(conf[key])

    def image(self, image: str) -> "DeploymentConfigBuilder":
        self._config["engine"]["image"] = image
        return self

    def replica_count(self, count: int) -> "DeploymentConfigBuilder":
        if (
            "autoscale" in self._config["engine"]
            and self._config["engine"]["autoscale"]["replica_max"] < count
        ):
            raise RuntimeError(
                "Replica count must be less than or equal to replica max. Use replica_autoscale_min_max to adjust this."
            )
        self._config["engine"]["replicas"] = count
        return self

    def _autoscale(self, autoscale: Dict[str, Any]):
        self._config["engine"]["autoscale"] = autoscale
        return self

    def replica_autoscale_min_max(self, maximum: int, minimum: int = 0):
        """Configures the minimum and maximum for autoscaling"""
        if minimum > maximum:
            raise RuntimeError("Minimum must be less than or equal to maximum")
        if minimum < 0:
            raise RuntimeError("Minimum must be at least 0")
        if "autoscale" not in self._config["engine"]:
            self._config["engine"]["autoscale"] = {}
        if (
            "replicas" in self._config["engine"]
            and self._config["engine"]["replicas"] > maximum
        ):
            raise RuntimeError(
                "Maximum must be greater than or equal to number of replicas"
            )
        self._config["engine"]["autoscale"]["replica_min"] = minimum
        self._config["engine"]["autoscale"]["replica_max"] = maximum
        self._config["engine"]["autoscale"]["type"] = "cpu"
        return self

    def autoscale_cpu_utilization(self, cpu_utilization_percentage: int):
        """Sets the average CPU metric to scale on in a percentage"""
        if "autoscale" not in self._config["engine"]:
            print(
                "Warn: min and max not set for autoscaling. These must be set to enable autoscaling"
            )
            self._config["engine"]["autoscale"] = {}
        self._config["engine"]["autoscale"][
            "cpu_utilization"
        ] = cpu_utilization_percentage
        return self

    def disable_autoscale(self):
        """Disables autoscaling in the deployment configuration"""
        if "autoscale" in ["engine"]:
            del self._config["engine"]["autoscale"]
        return self

    def _add_resource(
        self,
        component_stanza: Dict[str, Any],
        resource_name: str,
        value: Union[int, str],
    ) -> "DeploymentConfigBuilder":
        if "resources" not in component_stanza:
            component_stanza["resources"] = {"limits": {}, "requests": {}}
        component_stanza["resources"]["limits"][resource_name] = value
        component_stanza["resources"]["requests"][resource_name] = value
        return self

    def cpus(self, core_count: int) -> "DeploymentConfigBuilder":
        self._config["engine"]["cpu"] = core_count
        return self._add_resource(self._config["engine"], "cpu", core_count)

    def memory(self, memory_spec: str) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["engine"], "memory", memory_spec)

    def lb_cpus(self, core_count: int) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["enginelb"], "cpu", core_count)

    def lb_memory(self, memory_spec: int) -> "DeploymentConfigBuilder":
        return self._add_resource(self._config["enginelb"], "memory", memory_spec)

    def python_load_timeout_secs(self, timeout_secs: int) -> "DeploymentConfigBuilder":
        if "python" not in self._config["engine"]:
            self._config["engine"]["python"] = {}
        self._config["engine"]["python"]["load_timeout_millis"] = timeout_secs * 1000
        return self

    def _guarantee_sidekick_stanza(self, model: "Model") -> Dict[str, Any]:
        from .model import Model

        model_uid = model.uid()
        if model_uid not in self._config["engineAux"]["images"]:
            self._config["engineAux"]["images"][model_uid] = {}
        return self._config["engineAux"]["images"][model_uid]

    def sidekick_cpus(
        self, model: "Model", core_count: int
    ) -> "DeploymentConfigBuilder":
        """Sets the number of CPUs to be used for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param Model model: The sidekick model to configure.
        :param int core_count: Number of CPU cores to use in this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""
        from .model import Model

        return self._add_resource(
            self._guarantee_sidekick_stanza(model), "cpu", core_count
        )

    def sidekick_memory(
        self, model: "Model", memory_spec: str
    ) -> "DeploymentConfigBuilder":
        """Sets the memory to be used for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param Model model: The sidekick model to configure.
        :param str memory_spec: Specification of amount of memory (e.g., "2Gi", "500Mi") to use in
        this sidekick.
        :return: This DeploymentConfigBuilder instance for chaining."""
        from .model import Model
        from .model import Model

        return self._add_resource(
            self._guarantee_sidekick_stanza(model), "memory", memory_spec
        )

    def sidekick_env(
        self, model: "Model", environment: Dict[str, str]
    ) -> "DeploymentConfigBuilder":
        """Sets the environment variables to be set for the model's sidekick container. Only affects
        image-based models (e.g. MLFlow models) in a deployment.

        :param Model model: The sidekick model to configure.
        :param Dict[str, str] environment: Dictionary of environment variables names and their
        corresponding values to be set in the sidekick container.
        :return: This DeploymentConfigBuilder instance for chaining."""
        from .model import Model

        stanza = self._guarantee_sidekick_stanza(model)
        stanza["env"] = []
        for name, value in environment.items():
            stanza["env"].append({"name": name, "value": value})

        return self

    def build(self) -> DeploymentConfig:
        return DeploymentConfig(self._config)
