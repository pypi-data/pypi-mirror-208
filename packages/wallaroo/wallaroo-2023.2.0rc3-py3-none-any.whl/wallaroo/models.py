from .object import (
    Object,
    RequiredAttributeMissing,
    value_if_present,
    DehydratedValue,
    rehydrate,
)
from typing import TYPE_CHECKING, cast, Any, Dict, List, Optional
import gql
from dateutil import parser as dateparse
import datetime
from .model import Model
from .unwrap import unwrap
from .wallaroo_ml_ops_api_client.api.model import models_get
from .wallaroo_ml_ops_api_client.models import models_get_json_body
from .wallaroo_ml_ops_api_client.models.models_get_response_500 import (
    ModelsGetResponse500,
)


if TYPE_CHECKING:
    # Imports that happen below in methods to fix circular import dependency
    # issues need to also be specified here to satisfy mypy type checking.
    from .model_config import ModelConfig
    from .client import Client
    from .deployment import Deployment
    from .pipeline import Pipeline
    from .model import Model


class Models(Object):
    """
    A Wallaroo Model object. Models may have multiple versions, accessed via .versions()
    """

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
                "versions": len(self.versions()),
                "owner_id": self.owner_id(),
                "last_update_time": self.last_update_time(),
                "created_at": self.created_at(),
            }
        )

    def _repr_html_(self) -> str:
        return f"""
          <table>
            <tr>
              <th>Name</td>
              <td>{self.name()}</td>
            </tr>
            <tr>
              <th># of Versions</td>
              <td>{len(self.versions())}</td>
            </tr>
            <tr>
              <th>Owner ID</td>
              <td>{self.owner_id()}</td>
            </tr>
            <tr>
              <th>Last Updated</td>
              <td>{self.last_update_time()}</td>
            </tr>
            <tr>
              <th>Created At</td>
              <td>{self.created_at()}</td>
            </tr>
          </table>
        """

    def _fill(self, data: Dict[str, Any]) -> None:
        """Fills an object given a response dictionary from the GraphQL API.

        Only the primary key member must be present; other members will be
        filled in via rehydration if their corresponding member function is
        called.
        """
        for required_attribute in ["id"]:
            if required_attribute not in data:
                raise RequiredAttributeMissing(
                    self.__class__.__name__, required_attribute
                )
        # Required
        self._id = data["id"]

        # Optional
        self._name = value_if_present(data, "name")
        self._owner_id = value_if_present(data, "owner_id")
        self._created_at = (
            dateparse.isoparse(data["created_at"])
            if "created_at" in data
            else DehydratedValue()
        )
        self._last_update_time = (
            dateparse.isoparse(data["updated_at"])
            if "updated_at" in data
            else DehydratedValue()
        )

        self._versions = (
            [Model(client=self.client, data=x) for x in data["models"]]
            if "models" in data
            else DehydratedValue()
        )

    def _fetch_attributes(self) -> Dict[str, Any]:
        """Fetches all member data from the GraphQL API."""
        client = unwrap(self.client)
        ret = models_get.sync(
            client=client.mlops(),
            json_body=models_get_json_body.ModelsGetJsonBody(self.id()),
        )

        if isinstance(ret, ModelsGetResponse500):
            raise RuntimeError(ret.msg)

        if ret is None:
            raise RuntimeError("An error occurred loading the model.")

        return ret.to_dict()

    def id(self) -> int:
        return self._id

    @rehydrate("_name")
    def name(self) -> str:
        return cast(str, self._name)

    @rehydrate("_owner_id")
    def owner_id(self) -> str:
        return cast(str, self._owner_id)

    @rehydrate("_last_update_time")
    def last_update_time(self) -> datetime.datetime:
        return cast(datetime.datetime, self._last_update_time)

    @rehydrate("_created_at")
    def created_at(self) -> datetime.datetime:
        return cast(datetime.datetime, self._created_at)

    @rehydrate("_versions")
    def versions(self) -> List["Model"]:
        return cast(List["Model"], self._versions)


class ModelsList(List[Models]):
    """Wraps a list of Models for display in a display-aware environment like Jupyter."""

    def _repr_html_(self) -> str:
        def row(models: Models):
            return f"""
            <tr>
              <td>{models.name()}</td>
              <td>{len(models.versions())}</td>
              <td>{models.owner_id()}</td>
              <td>{models.last_update_time()}</td>
              <td>{models.created_at()}</td>
            </tr>
          """

        return f"""
          <table>
            <tr>
              <th>Name</th>
              <th># of Versions</th>
              <th>Owner ID</th>
              <th>Last Updated</th>
              <th>Created At</th>
            </tr>
            {" ".join([row(models) for models in self])}
          </table>
        """
