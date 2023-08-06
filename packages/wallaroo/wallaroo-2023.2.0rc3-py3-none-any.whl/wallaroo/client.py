import base64
import json
import math
import os
import pathlib
import posixpath
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from functools import partial
from itertools import chain, repeat
from typing import Any, Dict, List, NewType, Optional, TextIO, Tuple, Union, cast
from urllib.parse import quote_plus

import gql  # type: ignore
import pandas as pd
import pyarrow as pa  # type: ignore
import requests
from gql.transport.requests import RequestsHTTPTransport

from wallaroo.models import Models, ModelsList

from . import auth
from .assay import Assay, AssayAnalysis, AssayAnalysisList, Assays
from .assay_config import AssayBuilder, AssayConfig
from .checks import require_dns_compliance
from .datasizeunit import DataSizeUnit
from .deployment import Deployment
from .framework import Framework
from .inference_decode import inference_logs_to_dataframe, nested_df_to_flattened_df
from .logs import LogEntries, LogEntry
from .model import Model, ModelVersions
from .model_config import ModelConfig
from .ModelConversion import (
    ConvertKerasArguments,
    ConvertSKLearnArguments,
    ConvertXGBoostArgs,
    ModelConversionArguments,
    ModelConversionFailure,
    ModelConversionGenericException,
    ModelConversionSource,
    ModelConversionSourceFileNotPresent,
    ModelConversionUnsupportedType,
)
from .object import (
    EntityNotFoundError,
    ModelConversionError,
    ModelConversionTimeoutError,
    ModelUploadError,
)
from .orchestration import Orchestration
from .pipeline import Pipeline, Pipelines
from .pipeline_config import PipelineConfig
from .pipeline_variant import PipelineVariant, PipelineVariants
from .tag import Tag, Tags
from .task import Task
from .user import User
from .utils import create_new_file, is_arrow_enabled, is_models_enabled, write_to_file
from .version import _user_agent
from .visibility import _Visibility
from .wallaroo_ml_ops_api_client.api.assay import (
    assays_create,
    assays_get_assay_results,
    assays_list,
)
from .wallaroo_ml_ops_api_client.api.model import models_list
from .wallaroo_ml_ops_api_client.api.pipeline import pipelines_create
from .wallaroo_ml_ops_api_client.api.workspace import workspaces_list
from .wallaroo_ml_ops_api_client.client import AuthenticatedClient
from .wallaroo_ml_ops_api_client.models import (
    assays_get_assay_results_json_body,
    models_list_json_body,
    pipelines_create_json_body,
    pipelines_create_json_body_definition,
    workspaces_list_json_body,
)
from .wallaroo_ml_ops_api_client.models.assays_create_json_body import (
    AssaysCreateJsonBody,
)
from .wallaroo_ml_ops_api_client.models.assays_create_response_200 import (
    AssaysCreateResponse200,
)
from .wallaroo_ml_ops_api_client.models.assays_get_assay_results_response_200_item import (
    AssaysGetAssayResultsResponse200Item,
)
from .wallaroo_ml_ops_api_client.models.assays_list_json_body import AssaysListJsonBody
from .wallaroo_ml_ops_api_client.models.models_list_response_200 import (
    ModelsListResponse200,
)
from .wallaroo_ml_ops_api_client.models.pipelines_create_response_200 import (
    PipelinesCreateResponse200,
)
from .wallaroo_ml_ops_api_client.models.workspaces_list_response_200 import (
    WorkspacesListResponse200,
)
from .wallaroo_ml_ops_api_client.types import UNSET
from .workspace import Workspace, Workspaces
from .connection import Connection, ConnectionList

Datetime = NewType("Datetime", datetime)

WALLAROO_SDK_AUTH_TYPE = "WALLAROO_SDK_AUTH_TYPE"
WALLAROO_SDK_AUTH_ENDPOINT = "WALLAROO_SDK_AUTH_ENDPOINT"
WALLAROO_URL = "WALLAROO_URL"
WALLAROO_AUTH_URL = "WALLAROO_AUTH_URL"

ARROW_CONTENT_TYPE = "application/vnd.apache.arrow.file"
JSON_CONTENT_TYPE = "application/json"
OCTET_STREAM_CONTENT_TYPE = "application/octet-stream"

UPLOAD_MODEL_STREAM_SUPPORTED_FLAVORS = [
    Framework.ONNX,
    Framework.TENSORFLOW,
    Framework.PYTHON,
]
DEFAULT_MODEL_CONVERSION_TIMEOUT = 60 * 10  # 10 minutes
DEFAULT_MODEL_CONVERSION_PYTHON_VERSION = "3.8"

DEFAULT_RECORDS_LIMIT = 100
DEFAULT_RECORDS_BY_TIME_LIMIT = 1_000_000
DEFAULT_MAX_DATA_SIZE = 100  # type: float
DEFAULT_MAX_DATA_UNIT = DataSizeUnit.MiB


class Client(object):
    """Client handle to a Wallaroo platform instance.

    Objects of this class serve as the entrypoint to Wallaroo platform
    functionality.
    """

    @staticmethod
    def get_urls(
        auth_type: Optional[str], api_endpoint: str, auth_endpoint: str
    ) -> Tuple[Optional[str], str, str]:
        """Method to calculate the auth values specified as defaults,
        as params or in ENV vars.
        Made static to be testable without reaching out to SSO, etc."""

        # If this is set, we are running in a pipeline orchestration deployment, meaning: we
        # override auth type because no other auth type provided in user code will work. Also, this
        # lets the user write a plain notebook and that does wallaroo.Client(auth_type=WHATEVER)
        # and upload it as an orchestration, and we will handle it silently.

        if os.getenv("WALLAROO_TASK_ID"):
            auth_type = "orch"

        elif auth_type is None:
            auth_type = os.environ.get(WALLAROO_SDK_AUTH_TYPE, None)

        # ideally we'd set auth_endpoint to None default value but that would
        # make the auth_endpoint type to be Optiona[str] which messes up
        # a lot| of type hinting and I wanted to make minimal changes without a
        # lot of 'warnings'.
        if len(auth_endpoint.strip()) == 0:
            auth_endpoint = (
                os.environ.get(WALLAROO_AUTH_URL)
                or os.environ.get(WALLAROO_SDK_AUTH_ENDPOINT)
                or "http://api-lb:8080"
            )

        api_endpoint = os.environ.get(WALLAROO_URL, api_endpoint)

        return auth_type, api_endpoint, auth_endpoint

    def __init__(
        self,
        api_endpoint: str = "http://api-lb:8080",
        auth_endpoint: str = "",
        request_timeout: Optional[int] = None,
        auth_type: Optional[str] = None,
        gql_client: Optional[gql.Client] = None,
        interactive: Optional[bool] = None,
        time_format: str = "%Y-%d-%b %H:%M:%S",
    ):
        """Create a Client handle.

        :param str api_endpoint: Host/port of the platform API endpoint
        :param str auth_endpoint: Host/port of the platform Keycloak instance
        :param int timeout: Max timeout of web requests, in seconds
        :param str auth_type: Authentication type to use. Can be one of: "none",
            "sso", "user_password".
        :param bool interactive: If provided and True, some calls will print additional human information, or won't when False. If not provided, interactive defaults to True if running inside Jupyter and False otherwise.
        :param str time_format: Preferred `strftime` format string for displaying timestamps in a human context.
        """

        auth_type, api_endpoint, auth_endpoint = Client.get_urls(
            auth_type, api_endpoint, auth_endpoint
        )

        self.auth = auth.create(auth_endpoint, auth_type)

        if request_timeout is None:
            request_timeout = int(os.getenv("WALLAROO_REQUEST_TIMEOUT", 45))

        if gql_client:
            self._gql_client = gql_client
        else:
            gql_transport = RequestsHTTPTransport(
                url=posixpath.join(api_endpoint, "v1/graphql"),
                auth=self.auth,
                timeout=request_timeout,
            )
            self._gql_client = gql.Client(
                transport=gql_transport, fetch_schema_from_transport=True
            )

        self.api_endpoint = api_endpoint

        self.auth_endpoint = auth_endpoint

        self.timeout = request_timeout

        self._setup_mlops_client()

        self._current_workspace: Optional[Workspace] = None

        # TODO: debate the names of these things
        self._default_ws_name: Optional[str] = None

        user_email = self.auth.user_email()
        if user_email is not None:
            self._default_ws_name = user_email + "_ws"

        if interactive is not None:
            self._interactive = interactive
        elif (
            "JUPYTER_SVC_SERVICE_HOST" in os.environ or "JUPYTERHUB_HOST" in os.environ
        ):
            self._interactive = True
        else:
            self._interactive = False

        self._time_format = time_format

        self._in_task = "WALLAROO_TASK_ID" in os.environ
        self._task_args_filename = "/home/jovyan/arguments.json"

    def _get_rest_api(self, path: str, params: dict):
        headers = {
            "authorization": self.auth._bearer_token_str(),
            "user-agent": _user_agent,
        }

        url = f"{self.api_endpoint}/{path}"

        return requests.get(url, headers=headers, params=params)

    def _post_rest_api(self, path: str, body: dict):
        headers = {
            "authorization": self.auth._bearer_token_str(),
            "user-agent": _user_agent,
        }

        url = f"{self.api_endpoint}/{path}"
        return requests.post(url, headers=headers, json=body)

    def list_tags(self) -> Tags:
        """List all tags on the platform.

        :return: A list of all tags on the platform.
        :rtype: List[Tag]
        """
        res = self._gql_client.execute(
            gql.gql(
                """
            query ListTags {
              tag(order_by: {id: desc}) {
                id
                tag
                model_tags {
                  model {
                    id
                    model_id
                    models_pk_id
                    model_version
                    
                  }
                }
                pipeline_tags {
                  pipeline {
                    id
                    pipeline_id
                    pipeline_versions {
                        id
                        version
                    }
                  }
                }
              }
            }


            """
            )
        )
        return Tags([Tag(client=self, data={"id": p["id"]}) for p in res["tag"]])

    def list_models(self) -> ModelsList:
        """List all models on the platform.

        :return: A list of all models on the platform.
        :rtype: List[Model]
        """
        id = self.get_current_workspace().id()
        res = models_list.sync(
            client=self.mlops(),
            json_body=models_list_json_body.ModelsListJsonBody(id),
        )

        if res is None:
            raise Exception("Failed to list models")

        if not isinstance(res, ModelsListResponse200):
            raise Exception(res.msg)

        return ModelsList([Models(client=self, data=v.to_dict()) for v in res.models])

    def list_deployments(self) -> List[Deployment]:
        """List all deployments (active or not) on the platform.

        :return: A list of all deployments on the platform.
        :rtype: List[Deployment]
        """
        res = self._gql_client.execute(
            gql.gql(
                """
            query ListDeployments {
              deployment {
                id
                deploy_id
                deployed
                deployment_model_configs {
                  model_config {
                    id
                  }
                }
              }
            }
            """
            )
        )
        return [Deployment(client=self, data=d) for d in res["deployment"]]

    """
        # Removed until we figure out what pipeline ownership means
        #
        # def search_my_pipelines(
        #     self,
        #     search_term: Optional[str] = None,
        #     deployed: Optional[bool] = None,
        #     created_start: Optional["Datetime"] = None,
        #     created_end: Optional["Datetime"] = None,
        #     updated_start: Optional["Datetime"] = None,
        #     updated_end: Optional["Datetime"] = None,
        # ) -> List[Pipeline]:
        #     user_id = self.auth.user_id()
        #     return Pipelines(
        #         self._search_pipelines(
        #             search_term,
        #             deployed,
        #             user_id,
        #             created_start,
        #             created_end,
        #             updated_start,
        #             updated_end,
        #         )
        #     )
    """

    def search_pipelines(
        self,
        search_term: Optional[str] = None,
        deployed: Optional[bool] = None,
        created_start: Optional["Datetime"] = None,
        created_end: Optional["Datetime"] = None,
        updated_start: Optional["Datetime"] = None,
        updated_end: Optional["Datetime"] = None,
    ) -> PipelineVariants:
        """Search for pipelines. All parameters are optional, in which case the result is the same as
        `list_pipelines()`. All times are strings to be parsed by `datetime.isoformat`. Example:

             myclient.search_pipelines(created_end='2022-04-19 13:17:59+00:00', search_term="foo")

        :param str search_term: Will be matched against tags and model names. Example: "footag123".
        :param bool deployed: Pipeline was deployed or not
        :param str created_start: Pipeline was created at or after this time
        :param str created_end: Pipeline was created at or before this time
        :param str updated_start: Pipeline was updated at or before this time
        :param str updated_end: Pipeline was updated at or before this time

        :return: A list of all pipelines on the platform.
        :rtype: List[Pipeline]
        """
        return PipelineVariants(
            self._search_pipelines(
                search_term,
                deployed,
                None,
                created_start,
                created_end,
                updated_start,
                updated_end,
            )
        )

    def _search_pipelines(
        self,
        search_term: Optional[str] = None,
        deployed: Optional[bool] = None,
        user_id: Optional[str] = None,
        created_start: Optional["Datetime"] = None,
        created_end: Optional["Datetime"] = None,
        updated_start: Optional["Datetime"] = None,
        updated_end: Optional["Datetime"] = None,
    ) -> List[PipelineVariant]:
        (query, params) = self._generate_search_pipeline_query(
            search_term=search_term,
            deployed=deployed,
            user_id=user_id,
            created_start=created_start,
            created_end=created_end,
            updated_start=updated_start,
            updated_end=updated_end,
        )
        q = gql.gql(query)
        data = self._gql_client.execute(q, variable_values=params)
        pipelines = []
        if data["search_pipelines"]:
            for p in data["search_pipelines"]:
                pipelines.append(PipelineVariant(self, p))
        return pipelines

    def _generate_search_pipeline_query(
        self,
        search_term: Optional[str] = None,
        deployed: Optional[bool] = None,
        user_id: Optional[str] = None,
        created_start: Optional["Datetime"] = None,
        created_end: Optional["Datetime"] = None,
        updated_start: Optional["Datetime"] = None,
        updated_end: Optional["Datetime"] = None,
    ):
        filters = []
        query_params = []
        params: Dict[str, Any] = {}
        search = ""
        if search_term:
            search = search_term
        params["search_term"] = search
        query_params.append("$search_term: String!")

        if user_id:
            filters.append("owner_id: {_eq: $user_id}")
            params["user_id"] = user_id
            query_params.append("$user_id: String!")

        if deployed is not None:
            filters.append("pipeline: {deployment: {deployed: {_eq: $deployed}}}")
            params["deployed"] = deployed
            query_params.append("$deployed: Boolean")

        self._generate_time_range_graphql(
            "created_at",
            start=created_start,
            end=created_end,
            filters=filters,
            query_params=query_params,
            params=params,
        )
        self._generate_time_range_graphql(
            "updated_at",
            start=updated_start,
            end=updated_end,
            filters=filters,
            query_params=query_params,
            params=params,
        )

        where_clause_str = self._generate_where_clause_str(filters)
        query_param_str = self._generate_query_param_str(query_params)
        query = f"""
            query GetPipelines({query_param_str}) {{
                search_pipelines(args: {{search: $search_term}}, distinct_on: id{where_clause_str}, order_by: {{id: desc}}) {{
                    id
                    created_at
                    pipeline_pk_id
                    updated_at
                    version
                    pipeline {{
                        id
                        pipeline_id
                        pipeline_tags {{
                            id
                            tag {{
                                id
                                tag
                            }}
                        }}
                    }}
                }}
            }}
        """
        return (query, params)

    def _generate_where_clause_str(self, filters: List[str]) -> str:
        where_clause_str = ""
        filters_len = len(filters)
        if filters_len > 0:
            if filters_len > 1:
                where_clause_str = f""", where: {{_and: {{ {", ".join(filters)} }}}}"""
            else:
                where_clause_str = f", where: {{{filters[0]}}}"
        return where_clause_str

    def _generate_query_param_str(self, query_params: List[str]):
        return ", ".join(query_params)

    def _generate_time_range_graphql(
        self,
        field: str,
        start: Optional["Datetime"],
        end: Optional["Datetime"],
        filters: List[str],
        query_params: List[str],
        params: Dict[str, Any],
    ):
        if start and not end:
            filters.append(f"{field}: {{_gte: $start_{field}}}")
            params[f"start_{field}"] = start
            query_params.append(f"$start_{field}: timestamptz!")
        elif end and not start:
            filters.append(f"{field}: {{_lte: $end_{field}}}")
            params[f"end_{field}"] = end
            query_params.append(f"$end_{field}: timestamptz!")
        elif start and end:
            filters.append(f"{field}: {{_gte: $start_{field}, _lte: $end_{field}}}")
            params[f"start_{field}"] = start
            params[f"end_{field}"] = start
            query_params.append(f"$start_{field}: timestamptz!")
            query_params.append(f"$end_{field}: timestamptz!")

    def search_my_models(
        self,
        search_term: Optional[str] = None,
        uploaded_time_start: Optional["Datetime"] = None,
        uploaded_time_end: Optional["Datetime"] = None,
    ) -> ModelVersions:
        """Search models owned by you
        params:
             search_term: Searches the following metadata: names, shas, versions, file names, and tags
             uploaded_time_start: Inclusive time of upload
             uploaded_time_end: Inclusive time of upload
        """
        user_id = self.auth.user_id()
        return ModelVersions(
            self._search_models(
                search_term=search_term,
                user_id=user_id,
                start=uploaded_time_start,
                end=uploaded_time_end,
            )
        )

    def search_models(
        self,
        search_term: Optional[str] = None,
        uploaded_time_start: Optional["Datetime"] = None,
        uploaded_time_end: Optional["Datetime"] = None,
    ) -> ModelVersions:
        """Search all models you have access to.
        params:
             search_term: Searches the following metadata: names, shas, versions, file names, and tags
             uploaded_time_start: Inclusive time of upload
             uploaded_time_end: Inclusive time of upload
        """
        return ModelVersions(
            self._search_models(
                search_term=search_term,
                start=uploaded_time_start,
                end=uploaded_time_end,
            )
        )

    def _search_models(
        self, search_term=None, user_id=None, start=None, end=None
    ) -> List[Model]:
        (query, params) = self._generate_model_query(
            search_term=search_term,
            user_id=user_id,
            start=start,
            end=end,
        )

        q = gql.gql(query)

        data = self._gql_client.execute(q, variable_values=params)
        models = []
        if data["search_models"]:
            for m in data["search_models"]:
                models.append(Model(self, m))
        return models

    def _generate_model_query(
        self,
        search_term=None,
        user_id=None,
        start=None,
        end=None,
    ):
        filters = []
        query_params = []
        params = {}
        search = ""
        if search_term:
            search = search_term
        params["search_term"] = search
        query_params.append("$search_term: String!")
        if user_id:
            filters.append("owner_id: {_eq: $user_id}")
            params["user_id"] = user_id
            query_params.append("$user_id: String!")

        self._generate_time_range_graphql(
            "created_at",
            start=start,
            end=end,
            filters=filters,
            params=params,
            query_params=query_params,
        )

        where_clause_str = self._generate_where_clause_str(filters)
        query_param_str = self._generate_query_param_str(query_params)
        query = f"""
            query GetModels({query_param_str}) {{
              search_models(args: {{search: $search_term}}{where_clause_str}, order_by: {{created_at: desc}}) {{
                id
              }}
            }}
        """
        return (query, params)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Find a user by email"""
        assert email is not None
        escaped_email = quote_plus(email)
        url = (
            f"{self.auth_endpoint}/auth/admin/realms/master/users?email={escaped_email}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth._bearer_token_str(),
            "User-Agent": _user_agent,
        }
        resp = requests.get(url, headers=headers, data={})
        jresp = resp.json()
        return None if jresp == [] else User(client=self, data=jresp[0])

    def deactivate_user(self, email: str) -> None:
        """Deactivates an existing user of the platform

        Deactivated users cannot log into the platform.
        Deactivated users do not count towards the number of allotted user seats from the license.

        The Models and Pipelines owned by the deactivated user are not removed from the platform.

        :param str email: The email address of the user to deactivate.

        :return: None
        :rtype: None
        """

        if self.auth.user_email() == email:
            raise Exception("A user may not deactive themselves.")

        user = self.get_user_by_email(email)

        if user is None:
            raise EntityNotFoundError("User", {"email": email})

        if user.username() == "admin":
            raise Exception("Admin user may not be deactivated.")

        url = f"{self.auth_endpoint}/auth/admin/realms/master/users/{user._id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth._bearer_token_str(),
            "User-Agent": _user_agent,
        }

        # Get the current full user representation to return in the mutation due to keycloak bug
        get_user_response = requests.get(url, headers=headers, data={})

        cur_user_rep = get_user_response.json()
        cur_user_rep["enabled"] = False

        resp = requests.put(url, headers=headers, json=cur_user_rep)

        if resp.status_code != 204:
            raise EntityNotFoundError("User", {"email": email})
        return None

    def activate_user(self, email: str) -> None:
        """Activates an existing user of the platform that had been previously deactivated.

        Activated users can log into the platform.

        :param str email: The email address of the user to activate.

        :return: None
        :rtype: None
        """
        user = self.get_user_by_email(email)

        if user is None:
            raise EntityNotFoundError("User", {"email": email})

        url = f"{self.auth_endpoint}/auth/admin/realms/master/users/{user._id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth._bearer_token_str(),
            "User-Agent": _user_agent,
        }

        # Get the current full user representation to return in the mutation due to keycloak bug
        get_user_response = requests.get(url, headers=headers, data={})

        cur_user_rep = get_user_response.json()
        cur_user_rep["enabled"] = True

        resp = requests.put(url, headers=headers, json=cur_user_rep)

        if resp.status_code != 204:
            raise EntityNotFoundError("User", {"email": email})
        return None

    def _get_user_by_id(self, id: str) -> Optional[User]:
        assert id is not None
        url = f"{self.auth_endpoint}/auth/admin/realms/master/users/{id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth._bearer_token_str(),
            "User-Agent": _user_agent,
        }
        resp = requests.get(url, headers=headers, data={})
        jresp = resp.json()
        return None if jresp == [] else User(client=self, data=jresp)

    def list_users(self) -> List[User]:
        """List of all Users on the platform

        :return: A list of all Users on the platform.
        :rtype: List[User]
        """
        resp = User.list_users(
            auth=self.auth,
            api_endpoint=self.api_endpoint,
            auth_endpoint=self.auth_endpoint,
        )
        return [User(client=self, data=u) for u in resp]

    def upload_model(
        self,
        name: str,
        path: Union[str, pathlib.Path],
        framework: Optional[Framework] = None,
        input_schema: Optional[pa.Schema] = None,
        output_schema: Optional[pa.Schema] = None,
        convert_wait: Optional[bool] = True,
    ) -> Model:
        """Upload a model defined by a file as a new model variant.

        :param name: str The name of the model of which this is a variant.
            Names must be ASCII alpha-numeric characters or dash (-) only.
        :param path: Union[str, pathlib.Path] Path of the model file to upload.
        :param framework: Optional[Framework] Supported model frameworks.
            Use models from Framework Enum. Example: Framework.PYTORCH, Framework.TENSORFLOW
        :param input_schema: Optional pa.Schema Input schema, required for flavors other than ONNX, Tensorflow, and Python
        :param output_schema: Optional pa.Schema Output schema, required for flavors other than ONNX, Tensorflow, and Python
        :param convert_wait: Optional bool Defaults to True. Specifies if method should return when conversion is over or not.
        :return: The created Model.
        :rtype: Model
        """
        require_dns_compliance(name)
        payload = {
            "name": name,
            "visibility": _Visibility.PRIVATE,
            "workspace_id": self.get_current_workspace().id(),
        }

        if isinstance(path, str):
            path = pathlib.Path(path)

        with path.open("rb") as f:
            if not is_models_enabled():
                return self._upload_model_stream(path.name, payload, f)

            if not isinstance(framework, Framework):
                raise ValueError(
                    "framework must be a Framework Enum. Example: Framework.PYTORCH, Framework.TENSORFLOW"
                )

            payload["conversion"] = {
                "framework": framework.value,
                "python_version": DEFAULT_MODEL_CONVERSION_PYTHON_VERSION,
                "requirements": [],
            }

            if framework in UPLOAD_MODEL_STREAM_SUPPORTED_FLAVORS:
                return self._upload_model_via_models_service(
                    path.name, payload, f, False
                )

            if input_schema is None:
                raise Exception("parameter 'input_schema' required for this framework")
            if output_schema is None:
                raise Exception("parameter 'output_schema' required for this framework")

            payload["input_schema"] = base64.b64encode(
                bytes(input_schema.serialize())
            ).decode("utf8")
            payload["output_schema"] = base64.b64encode(
                bytes(output_schema.serialize())
            ).decode("utf8")
            return self._upload_model_via_models_service(
                path.name, payload, f, True, convert_wait
            )

    def _upload_model_stream(
        self, filename: str, data: Dict[str, Any], file: Any
    ) -> Model:
        endpoint = posixpath.join(self.api_endpoint, "v1/api/models/upload_stream")
        payload = {"filename": filename, **data}
        headers = {"User-Agent": _user_agent}

        res = requests.post(
            endpoint, auth=self.auth, params=payload, data=file, headers=headers
        )
        if res.status_code != 200:
            raise ModelUploadError(res.text)

        res_dict = json.loads(res.text)
        return Model(self, data=res_dict["insert_models"]["returning"][0]["models"][0])

    def _upload_model_via_models_service(
        self,
        filename: str,
        data: Dict[str, Any],
        file: Any,
        convert: Optional[bool] = True,
        convert_wait: Optional[bool] = True,
    ) -> Model:
        """
        Upload and (possibly) convert a model defined by a file as a new model variant. If convert_wait
        is True, the method will wait for about 10min for the conversion to finish before returning.
        If convert_wait is False, the method will return immediately.
        """
        files = {
            "metadata": (None, json.dumps(data), JSON_CONTENT_TYPE),
            "file": (filename, file, OCTET_STREAM_CONTENT_TYPE),
        }
        headers = {"User-Agent": _user_agent}
        route = "upload_and_convert" if convert else "upload"
        endpoint = posixpath.join(self.api_endpoint, f"v1/api/models/{route}")

        try:
            res = requests.post(endpoint, auth=self.auth, files=files, headers=headers)
            res.raise_for_status()
        except requests.exceptions.RequestException as request_err:
            raise request_err

        try:
            res_dict = json.loads(res.text)
        except (json.JSONDecodeError, ValueError) as json_err:
            raise ValueError("Decoding response from model upload failed") from json_err

        model = Model(self, data=res_dict["insert_models"]["returning"][0]["models"][0])
        if convert is not True or convert_wait is not True:
            return self._get_configured_model_version(model)
        else:
            return self._wait_for_model(model)

    def _wait_for_model(self, model: Model) -> Model:
        poll_interval = 5
        expire_time = datetime.now() + timedelta(
            seconds=DEFAULT_MODEL_CONVERSION_TIMEOUT
        )
        print(
            f"Waiting for model conversion... It may take up to {DEFAULT_MODEL_CONVERSION_TIMEOUT/60}min."
        )
        print(f"Model is ", end="", flush=True)
        last_status = None
        while datetime.now() < expire_time:
            model = self._get_configured_model_version(model)
            status = model.status().lower()
            if status == "ready":
                print("Ready.")
                return model
            elif status == "error":
                print("ERROR!")
                raise ModelConversionError(f"An error occured during model conversion.")
            else:
                if last_status != status:
                    print(
                        f"{status.replace('_', ' ').capitalize()}", end="", flush=True
                    )
                print(".", end="", flush=True)
                last_status = status
                time.sleep(poll_interval)
        else:
            raise ModelConversionTimeoutError(
                f"Model conversion timed out after {DEFAULT_MODEL_CONVERSION_TIMEOUT/60}min."
            )

    def _get_configured_model_version(self, model: Model) -> Model:
        headers = {"User-Agent": _user_agent}
        endpoint = posixpath.join(self.api_endpoint, "v1/api/models/get_version_by_id")
        params = {"model_version_id": model.id()}
        try:
            get_model_version_response = requests.post(
                endpoint, auth=self.auth, json=params, headers=headers
            )
            get_model_version_response.raise_for_status()
        except requests.exceptions.RequestException as request_err:
            raise request_err
        try:
            get_model_version_response_dict = json.loads(
                get_model_version_response.text
            )
        except (json.JSONDecodeError, ValueError) as json_err:
            raise ValueError(
                "Decoding response from models/get_version_by_id failed"
            ) from json_err

        model = Model(
            self,
            data=get_model_version_response_dict["model_version"]["model_version"],
        )
        model._config = ModelConfig(
            self,
            get_model_version_response_dict["model_version"]["config"],
        )
        return model

    def register_model_image(self, name: str, image: str) -> Model:
        """Registers an MLFlow model as a new model.

        :param str model_name: The name of the model of which this is a variant.
            Names must be ASCII alpha-numeric characters or dash (-) only.
        :param str image: Image name of the MLFlow model to register.
        :return: The created Model.
        :rtype: Model
        """
        data = {
            "image_path": image,
        }
        return self._upload_model(name, data)

    def _upload_model(
        self, name: str, data: Dict[str, Any], files: Dict[str, Tuple[str, bytes]] = {}
    ):
        require_dns_compliance(name)
        endpoint = posixpath.join(self.api_endpoint, "v1/api/models/upload")
        data = {**data, "name": name, "workspace_id": self.get_current_workspace().id()}
        if len(files) == 0:
            files = {"dummy": ("none", b"")}

        headers = {"User-Agent": _user_agent}

        res = requests.post(
            endpoint, files=files, auth=self.auth, data=data, headers=headers
        )
        if res.status_code != 200:
            raise ModelUploadError(res.text)

        res_dict = json.loads(res.text)
        return Model(self, data=res_dict["insert_models"]["returning"][0]["models"][0])

    def model_by_name(self, model_class: str, model_name: str) -> Model:
        """Fetch a Model by name.

        :param str model_class: Name of the model class.
        :param str model_name: Name of the variant within the specified model class.
        :return: The Model with the corresponding model and variant name.
        :rtype: Model
        """
        res = self._gql_client.execute(
            gql.gql(
                """
                query ModelByName($model_id: String!, $model_version: String!) {
                  model(where: {_and: [{model_id: {_eq: $model_id}}, {model_version: {_eq: $model_version}}]}) {
                    id
                    model_id
                    model_version
                  }
                }
                """
            ),
            variable_values={
                "model_id": model_class,
                "model_version": model_name,
            },
        )
        if not res["model"]:
            raise EntityNotFoundError(
                "Model", {"model_class": model_class, "model_name": model_name}
            )
        return Model(client=self, data={"id": res["model"][0]["id"]})

    def deployment_by_name(self, deployment_name: str) -> Deployment:
        """Fetch a Deployment by name.

        :param str deployment_name: Name of the deployment.
        :return: The Deployment with the corresponding name.
        :rtype: Deployment
        """
        res = self._gql_client.execute(
            gql.gql(
                """
                query DeploymentByName($deployment_name: String!) {
                  deployment(where: {deploy_id: {_eq: $deployment_name}}) {
                    id
                  }
                }
                """
            ),
            variable_values={
                "deployment_name": deployment_name,
            },
        )
        if not res["deployment"]:
            raise EntityNotFoundError(
                "Deployment", {"deployment_name": deployment_name}
            )
        return Deployment(client=self, data={"id": res["deployment"][0]["id"]})

    def pipelines_by_name(self, pipeline_name: str) -> List[Pipeline]:
        """Fetch Pipelines by name.

        :param str pipeline_name: Name of the pipeline.
        :return: The Pipeline with the corresponding name.
        :rtype: Pipeline
        """
        res = self._gql_client.execute(
            gql.gql(
                """
                query PipelineByName($pipeline_name: String!) {
                  pipeline(where: {pipeline_id: {_eq: $pipeline_name}}, order_by: {created_at: desc}) {
                    id
                  }
                }
                """
            ),
            variable_values={
                "pipeline_name": pipeline_name,
            },
        )
        assert "pipeline" in res
        length = len(res["pipeline"])
        if length < 1:
            raise EntityNotFoundError("Pipeline", {"pipeline_name": pipeline_name})
        return [Pipeline(client=self, data={"id": p["id"]}) for p in res["pipeline"]]

    def list_pipelines(self) -> List[Pipeline]:
        """List all pipelines on the platform.

        :return: A list of all pipelines on the platform.
        :rtype: List[Pipeline]
        """
        res = self._gql_client.execute(
            gql.gql(
                """
            query ListPipelines {
              pipeline(order_by: {id: desc}) {
                id
                pipeline_tags {
                  tag {
                    id
                    tag
                  }
                }
              }
            }
            """
            )
        )
        return Pipelines([Pipeline(client=self, data=d) for d in res["pipeline"]])

    def build_pipeline(self, pipeline_name: str) -> "Pipeline":
        """Starts building a pipeline with the given `pipeline_name`,
        returning a :py:PipelineConfigBuilder:

        When completed, the pipeline can be uploaded with `.upload()`

        :param pipeline_name string: Name of the pipeline, must be composed of ASCII
          alpha-numeric characters plus dash (-).
        """

        require_dns_compliance(pipeline_name)

        _Visibility.PRIVATE

        # TODO: Needs to handle visibility?
        data = pipelines_create.sync(
            client=self.mlops(),
            json_body=pipelines_create_json_body.PipelinesCreateJsonBody(
                pipeline_name,
                self.get_current_workspace().id(),
                pipelines_create_json_body_definition.PipelinesCreateJsonBodyDefinition.from_dict(
                    {}
                ),
            ),
        )

        if data is None:
            raise Exception("Failed to create pipeline")

        if not isinstance(data, PipelinesCreateResponse200):
            raise Exception(data.msg)

        return Pipeline(client=self, data={"id": data.pipeline_pk_id})

    def _upload_pipeline_variant(
        self,
        name: str,
        config: PipelineConfig,
    ) -> Pipeline:
        """Creates a new PipelineVariant with the specified configuration.

        :param str name: Name of the Pipeline. Must be unique across all Pipelines.
        :param config PipelineConfig: Pipeline configuration.
        """
        definition = config.to_json()
        _Visibility.PRIVATE

        data = pipelines_create.sync(
            client=self.mlops(),
            json_body=pipelines_create_json_body.PipelinesCreateJsonBody(
                name,
                self.get_current_workspace().id(),
                pipelines_create_json_body_definition.PipelinesCreateJsonBodyDefinition.from_dict(
                    definition
                ),
            ),
        )

        if data is None:
            # TODO: Generalize
            raise Exception("Failed to create pipeline")

        if not isinstance(data, PipelinesCreateResponse200):
            raise Exception(data.msg)

        for alert_config in config.alert_configurations:
            self._gql_client.execute(
                gql.gql(
                    """
                mutation CreateAlertConfiguration(
                    $pipeline_version_id: bigint,
                    $name: String,
                    $expression: String,
                    $notifications: jsonb
                ) {
                    insert_alert_configuration(objects: {
                        name: $name,
                        expression: $expression,
                        notifications: $notifications,
                        pipeline_version_pk_id: $pipeline_version_id
                    }) {
                        returning { id }
                    }
                }
                """
                ),
                variable_values={
                    **alert_config.to_json(),
                    "pipeline_version_id": data.pipeline_pk_id,
                },
            )

        pipeline_data = data.to_dict()
        pipeline_data["id"] = data.pipeline_pk_id

        return Pipeline(
            client=self,
            data=pipeline_data,
        )

    def create_value_split_experiment(
        self,
        name: str,
        meta_key: str,
        default_model: ModelConfig,
        challenger_models: List[Tuple[Any, ModelConfig]],
    ) -> Pipeline:
        """Creates a new PipelineVariant of a "value-split experiment" type.
        :param str name: Name of the Pipeline
        :param meta_key str: Inference input key on which to redirect inputs to
            experiment models.
        :param default_model ModelConfig: Model to send inferences by default.
        :param challenger_models List[Tuple[Any, ModelConfig]]: A list of
            meta_key values -> Models to send inferences. If the inference data
            referred to by meta_key is equal to one of the keys in this tuple,
            that inference is redirected to the corresponding model instead of
            the default model.
        """
        args = [meta_key, default_model.model().name()]
        for v, m in challenger_models:
            args.append(v)
            args.append(m.model().name())
        step = {
            "id": "metavalue_split",
            "operation": "map",
            "args": args,
        }
        definition = {"id": name, "steps": [step]}
        # TODO: This seems like a one-to-one replace, find appropriate test.
        data = self._gql_client.execute(
            gql.gql(
                """
            mutation CreatePipeline(
                $pipeline_id: String,
                $version: String,
                $definition: jsonb,
                $workspace_id: bigint
            ) {
                insert_pipeline(
                    objects: {
                    pipeline_versions: {
                        data: { definition: $definition }
                    }
                    pipeline_id: $pipeline_id
                    }
                ) {
                    returning {
                        id
                    }
                }
            }
            """
            ),
            variable_values={
                "pipeline_id": name,
                "definition": definition,
                "workspace_id": self.get_current_workspace().id(),
            },
        )
        return Pipeline(
            client=self,
            data=data["insert_pipeline"]["returning"][0],
        )

    @staticmethod
    def cleanup_arrow_data_for_display(arrow_data: pa.Table) -> pa.Table:
        """
        Cleans up the inference result and log data from engine / plateau for display (ux) purposes.
        """
        columns = []
        table_schema = []
        for column_name in arrow_data.column_names:
            column_data = arrow_data[column_name]
            column_schema = arrow_data.schema.field(column_name)
            if "time" == column_name:
                time_df = arrow_data["time"].to_pandas().copy()
                time_df = pd.to_datetime(time_df, unit="ms")
                column_data = pa.array(time_df)
                column_schema = pa.field("time", pa.timestamp("ms"))
            if "check_failures" == column_name:
                check_failures_df = arrow_data["check_failures"].to_pandas()
                column_data = pa.array(check_failures_df.apply(len))
                column_schema = pa.field("check_failures", pa.int8())
            columns.append(column_data)
            table_schema.append(column_schema)
        new_schema = pa.schema(table_schema)
        return pa.Table.from_arrays(columns, schema=new_schema)

    @staticmethod
    def _build_headers_and_params(
        limit: Optional[int] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        dataset: Optional[List[str]] = None,
        dataset_exclude: Optional[List[str]] = None,
        dataset_separator: Optional[str] = None,
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        headers = {"User-Agent": _user_agent}
        params = dict()
        if is_arrow_enabled():
            headers.update({"Accept": ARROW_CONTENT_TYPE})
            if start_datetime is None and end_datetime is None:
                params["page_size"] = limit if limit is not None else DEFAULT_RECORDS_LIMIT  # type: ignore
                params["order"] = "desc"  # type: ignore
            elif start_datetime is not None and end_datetime is not None:
                if limit is not None:
                    params["page_size"] = limit  # type: ignore
                start_str = start_datetime.astimezone(tz=timezone.utc).isoformat()
                params["time.start"] = start_str  # type: ignore
                end_str = end_datetime.astimezone(tz=timezone.utc).isoformat()
                params["time.end"] = end_str  # type: ignore
            else:
                raise Exception(
                    "Please provide both start datetime and end datetime together."
                )
            default_dataset_exclude = ["metadata"]
            if dataset is not None:
                if "metadata" in dataset:
                    default_dataset_exclude = []
            params["dataset[]"] = dataset or ["*"]  # type: ignore
            params["dataset.exclude[]"] = (
                [*dataset_exclude, *default_dataset_exclude]  # type: ignore
                if dataset_exclude
                else default_dataset_exclude
            )
            params["dataset.separator"] = dataset_separator or "."  # type: ignore
        else:
            params["limit"] = limit if limit is not None else DEFAULT_RECORDS_LIMIT  # type: ignore
            headers.update({"Accept": JSON_CONTENT_TYPE})
        return headers, params

    def _get_next_records(
        self,
        params: Optional[Dict[str, Any]],
        iterator: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, Any]],
        base: str,
    ) -> requests.Response:
        try:
            resp = requests.post(
                base + "/records",
                params=params,
                json=iterator,
                auth=self.auth,
                headers=headers,
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise requests.exceptions.HTTPError(http_error, resp.text)
        return resp

    def _extract_logs_from_response(
        self, resp: requests.Response
    ) -> Tuple[pa.Table, Dict[str, Any], str]:
        with pa.ipc.open_file(resp.content) as reader:
            entries = reader.read_all()
            metadata_dict = reader.schema.metadata
            metadata = (
                json.loads(metadata_dict[b"status"])
                if metadata_dict is not None
                else None
            )
            status = metadata["status"] if metadata is not None else None
            if entries.num_rows > 0:
                clean_entries = self.cleanup_arrow_data_for_display(entries)
                iterator = metadata["next"] if "next" in metadata else None
                return clean_entries, iterator, status
            else:
                iterator = None
                return entries, iterator, status

    @staticmethod
    def _slice_log_results_if_exceeds_limit(
        logs_table: pa.Table, rows_written: int, limit: Optional[int] = None
    ) -> Tuple[pa.Table, int, bool]:
        if limit is not None and rows_written >= limit:
            return (
                logs_table.slice(0, limit - (rows_written - logs_table.num_rows)),
                limit,
                True,
            )
        return logs_table, rows_written, False

    @staticmethod
    def _should_stop_log_collection(
        status: str,
        data_size_exceeded: bool,
        rows_written: int,
        end_time: str,
        data_size: float,
        data_unit: DataSizeUnit,
        is_sliced: bool,
        chronological_order: str,
    ) -> bool:
        if data_size_exceeded:
            sys.stderr.write(
                f"Warning: Pipeline log data size limit of {data_size} {data_unit.value} exceeded."
                f" {rows_written} {chronological_order} records exported successfully, {chronological_order}"
                f" record seen was at {end_time}. Set a different limit using data_size_limit for more data."
                f" Please request additional files separately.\n\n"
            )
            return True
        if status == "RecordLimited":
            sys.stderr.write(
                f"Warning: There are more logs available."
                f" Please set a larger limit to export more data.\n\n"
            )
            return True
        if status == "All":
            return True
        if is_sliced:
            return True

        return False

    def _process_logs(
        self, logs_table: pa.Table, rows_written: int, limit: Optional[int]
    ) -> Tuple[pa.Table, int, bool, str]:
        rows_written += logs_table.num_rows
        (
            logs_table,
            total_rows_written,
            is_sliced,
        ) = self._slice_log_results_if_exceeds_limit(logs_table, rows_written, limit)
        end_time = (
            logs_table.column("time")[-1].as_py() if logs_table.num_rows > 0 else None
        )
        return logs_table, total_rows_written, is_sliced, end_time

    @staticmethod
    def _validate_file_size_input(data_size_limit: str) -> Tuple[float, DataSizeUnit]:
        pattern = r"^(\d+(\.\d+)?)\s*([KMGT]iB)$"
        match = re.match(pattern, data_size_limit, re.IGNORECASE)

        if not match:
            raise ValueError(
                "Invalid data size format. Please use the format: <number><unit> (e.g. 1.5MiB or 1 GiB)"
            )

        size = float(match.group(1))
        unit = DataSizeUnit.from_string(match.group(3).strip())

        if size <= 0:
            raise ValueError("File size must be positive.")

        return size, unit

    def _export_logs(
        self,
        base: str,
        params: Dict[str, Any],
        headers: Dict[str, str],
        directory: str,
        file_prefix: str,
        data_size_limit: Optional[str] = None,
        limit: Optional[int] = None,
        arrow: Optional[bool] = False,
    ) -> None:
        iterator = {}  # type: Dict[str, Any]

        chronological_order = (
            "oldest" if "time.start" and "time.end" in params else "newest"
        )
        data_size, data_unit = (
            self._validate_file_size_input(data_size_limit)
            if data_size_limit
            else (DEFAULT_MAX_DATA_SIZE, DEFAULT_MAX_DATA_UNIT)
        )
        data_size_limit_in_bytes = data_unit.calculate_bytes(data_size)

        rows_written = 0
        writer = None
        file_num = 0
        schema = None
        schema_changed = False
        end_time = None
        previous_end_time = None
        data_size_exceeded = False
        total_data_size = 0

        while iterator is not None:
            response = self._get_next_records(params, iterator, headers, base)
            logs_table, iterator, status = self._extract_logs_from_response(response)
            if logs_table.num_rows == 0:
                break
            if schema is not None and schema != logs_table.schema:
                schema_changed = True
                writer.close()
                writer = None

            if writer is None:
                schema = logs_table.schema
                file_num += 1
                writer = create_new_file(
                    directory, file_num, file_prefix, schema, arrow
                )

            if end_time is None:
                previous_end_time = logs_table.column("time")[-1].as_py()

            sliced_table, rows_written, is_sliced, sliced_end_time = self._process_logs(
                logs_table, rows_written, limit
            )

            end_time = (
                sliced_end_time if sliced_end_time is not None else previous_end_time
            )
            for record_batch in sliced_table.to_batches():
                total_data_size += record_batch.nbytes
                write_to_file(record_batch, writer, arrow)
                if total_data_size > data_size_limit_in_bytes:
                    data_size_exceeded = True
                    break

            if self._should_stop_log_collection(
                status,
                data_size_exceeded,
                rows_written,
                end_time,
                data_size,
                data_unit,
                is_sliced,
                chronological_order,
            ):
                writer.close()
                break
        if schema_changed:
            sys.stderr.write(
                f"Note: The logs with different schemas are "
                f"written to separate files in the provided directory."
            )
        return None

    def get_logs(
        self,
        topic: str,
        limit: Optional[int] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        dataset: Optional[List[str]] = None,
        dataset_exclude: Optional[List[str]] = None,
        dataset_separator: Optional[str] = None,
        directory: Optional[str] = None,
        file_prefix: Optional[str] = None,
        data_size_limit: Optional[str] = None,
        arrow: Optional[bool] = False,
    ) -> Tuple[Union[pa.Table, pd.DataFrame, LogEntries, None], Optional[str]]:
        """
        Get logs for the given topic.
        :param topic: str The topic to get logs for.
        :param limit: Optional[int] The maximum number of logs to return.
        :param start_datetime: Optional[datetime] The start time to get logs for.
        :param end_datetime: Optional[datetime] The end time to get logs for.
         :param dataset: Optional[List[str]] By default this is set to ["*"] which returns,
            ["time", "in", "out", "check_failures"]. Other available options - ["metadata"]
        :param dataset_exclude: Optional[List[str]] If set, allows user to exclude parts of dataset.
        :param dataset_separator: Optional[Union[Sequence[str], str]] If set to ".", return dataset will be flattened.
        :param directory: Optional[str] If set, logs will be exported to a file in the given directory.
        :param file_prefix: Optional[str] Prefix to name the exported file. By default, the file_prefix will be set to
            the pipeline name.
        :param data_size_limit: Optional[str] The maximum size of the exported data in MB.
            Size includes all files within the provided directory. By default, the data_size_limit will be set to 100MB.
        :param arrow: Optional[bool] If set to True, return logs as an Arrow Table. Else, returns Pandas DataFrame.
        :return: Tuple[Union[pa.Table, pd.DataFrame, LogEntries], str] The logs and status.
        """
        base = self.api_endpoint + f"/v1/logs/topic/" + topic

        headers, params = self._build_headers_and_params(
            limit=limit,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            dataset=dataset,
            dataset_exclude=dataset_exclude,
            dataset_separator=dataset_separator,
        )
        if file_prefix is not None and directory is not None:
            self._export_logs(
                base=base,
                directory=directory,
                file_prefix=file_prefix,
                data_size_limit=data_size_limit,
                params=params,
                headers=headers,
                limit=limit,
                arrow=arrow,
            )
            return None, None
        if is_arrow_enabled():
            response = self._get_next_records(
                params=params, iterator={}, headers=headers, base=base
            )
            entries, _, status = self._extract_logs_from_response(response)
            return entries if arrow else entries.to_pandas(), status
        else:
            if limit is None:
                limit = DEFAULT_RECORDS_LIMIT
            response_parts = requests.get(base, auth=self.auth)
            partitions = response_parts.json()["partitions"]

            iterator = {
                k: max(0, span["end"] - math.floor(limit / len(partitions)))
                for k, span in partitions.items()
            }
            response = self._get_next_records(
                params=params, iterator=iterator, headers=headers, base=base
            )
            response_json = response.json()
            return (
                LogEntries([LogEntry(json.loads(l)) for l in response_json["records"]]),
                response_json.get("status", "None"),
            )

    def security_logs(self, limit: int) -> List[dict]:
        """This function is not available in this release"""
        raise RuntimeError("security_log() is not available in this release.")

    def get_raw_logs(
        self,
        topic: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100_000,
        parse: bool = False,
        dataset: Optional[List[str]] = None,
        dataset_exclude: Optional[List[str]] = None,
        dataset_separator: Optional[str] = None,
        verbose: bool = False,
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """Gets logs from Plateau for a particular time window without attempting
        to convert them to Inference LogEntries. Logs can be returned as strings
        or the json parsed into lists and dicts.
        :param topic str: The name of the topic to query
        :param start Optional[datetime]: The start of the time window
        :param end Optional[datetime]: The end of the time window
        :param limit int: The number of records to retrieve. Note retrieving many
            records may be a performance bottleneck.
        :param parse bool: Wether to attempt to parse the string as a json object.
        :param verbose bool: Prints out info to help diagnose issues.
        """

        assert limit <= 1_000_000

        base = self.api_endpoint + f"/v1/logs/topic/" + topic
        headers = {"User-Agent": _user_agent}
        resp = requests.get(base, auth=self.auth, headers=headers)
        if resp.status_code != 200:
            raise EntityNotFoundError(
                f"Could not get partitions {resp.text}", {"url": base}
            )
        data = resp.json()
        partitions = data["partitions"]

        if verbose:
            print(f"Got partitions {partitions}")

        params: Dict[str, Any] = {"page_size": limit}
        if start is not None:
            start_str = start.astimezone(tz=timezone.utc).isoformat()
            params["time.start"] = start_str
        if end is not None:
            end_str = end.astimezone(tz=timezone.utc).isoformat()
            params["time.end"] = end_str

        if len(partitions) == 0:
            next: Optional[Dict[str, int]] = None
        else:
            sizes = [
                sz + excess
                for sz, excess in zip(
                    repeat(limit // len(partitions), len(partitions)),
                    chain(repeat(1, limit % len(partitions)), repeat(0)),
                )
            ]

            next = {
                k: max(0, span["end"] - sz)
                for (k, span), sz in zip(partitions.items(), sizes)
            }

        if is_arrow_enabled():
            headers.update({"Accept": ARROW_CONTENT_TYPE})
            params["dataset[]"] = dataset or ["*"]
            if dataset_exclude is not None:
                params["dataset.exclude[]"] = dataset_exclude
            if dataset_separator is not None:
                params["dataset.separator"] = dataset_separator  # type: ignore
        else:
            headers.update({"Accept": JSON_CONTENT_TYPE})

        if verbose:
            print("Using params: ", params)
            print("Using iterators: ", next)

        records = []
        while next is not None:
            resp = requests.post(
                base + "/records",
                params=params,
                json=next,
                auth=self.auth,
                headers=headers,
            )
            if resp.status_code != 200:
                raise EntityNotFoundError(
                    f"Could not get records {resp.text}",
                    {"url": base, "params": str(params), "iterator": str(next)},
                )

            if verbose:
                print("response: ", resp)

            if is_arrow_enabled():
                with pa.ipc.open_file(resp.content) as reader:
                    entries_df = reader.read_pandas()
                    if len(entries_df) > 0:
                        records.append(entries_df)
                        next = json.loads(reader.schema.metadata[b"status"])["next"]
                    else:
                        next = None
            else:
                result = resp.json()
                result_records = result["records"]
                if len(result_records) > 0:
                    records.extend(result_records)
                    next = result["next"]
                else:
                    next = None

        if is_arrow_enabled():
            return pd.concat(records) if len(records) > 0 else pd.DataFrame()
        if parse:
            return [json.loads(r) for r in records]
        return records

    def get_raw_pipeline_inference_logs(
        self,
        topic: str,
        start: datetime,
        end: datetime,
        model_name: Optional[str] = None,
        limit: int = 100_000,
        verbose: bool = False,
    ) -> List[Union[Dict[str, Any], pd.DataFrame]]:
        """Gets logs from Plateau for a particular time window and filters them for
        the model specified.
        :param pipeline_name str: The name/pipeline_id of the pipeline to query
        :param topic str: The name of the topic to query
        :param start Optional[datetime]: The start of the time window
        :param end Optional[datetime]: The end of the time window
        :param model_id: The name of the specific model to filter if any
        :param limit int: The number of records to retrieve. Note retrieving many
            records may be a performance bottleneck.
        :param verbose bool: Prints out info to help diagnose issues.
        """
        logs = self.get_raw_logs(
            topic,
            start=start,
            end=end,
            limit=limit,
            parse=True,
            verbose=verbose,
        )

        if verbose:
            print(f"Got {len(logs)} initial logs")

        if len(logs) == 0:
            return logs

        if model_name:
            if isinstance(logs, pd.DataFrame):
                logs = logs[
                    logs["metadata"].map(
                        lambda md: json.loads(md["last_model"])["model_name"]
                    )
                    == model_name
                ]
            else:
                logs = [l for l in logs if l["model_name"] == model_name]

        # inference results are a unix timestamp in millis - filter by that
        start_ts = int(start.timestamp() * 1000)
        end_ts = int(end.timestamp() * 1000)

        if isinstance(logs, pd.DataFrame):
            logs = logs[(start_ts <= logs["time"]) & (logs["time"] < end_ts)]
        else:
            logs = [l for l in logs if start_ts <= l["time"] < end_ts]

        return logs

    def get_pipeline_inference_dataframe(
        self,
        topic: str,
        start: datetime,
        end: datetime,
        model_name: Optional[str] = None,
        limit: int = 100_000,
        verbose=False,
    ) -> pd.DataFrame:
        logs = self.get_raw_pipeline_inference_logs(
            topic, start, end, model_name, limit, verbose
        )
        if isinstance(logs, pd.DataFrame):
            return nested_df_to_flattened_df(logs)

        return inference_logs_to_dataframe(logs)

    def get_assay_results(
        self,
        assay_id: int,
        start: datetime,
        end: datetime,
    ) -> AssayAnalysisList:
        """Gets the assay results for a particular time window, parses them, and returns an
        AssayAnalysisList of AssayAnalysis.
        :param assay_id int: The id of the assay we are looking for.
        :param start datetime: The start of the time window
        :param end datetime: The end of the time window
        """
        res = assays_get_assay_results.sync(
            client=self.mlops(),
            json_body=assays_get_assay_results_json_body.AssaysGetAssayResultsJsonBody(
                assay_id, start, end
            ),
        )

        if res is None:
            raise Exception("Failed to list models")

        if not isinstance(res, List):
            raise Exception(res.msg)

        if len(res) != 0 and not isinstance(
            res[0], AssaysGetAssayResultsResponse200Item
        ):
            raise Exception("invalid response")

        return AssayAnalysisList([AssayAnalysis(v.to_dict()) for v in res])

    def build_assay(
        self,
        assay_name: str,
        pipeline: Pipeline,
        model_name: str,
        baseline_start: datetime,
        baseline_end: datetime,
    ) -> AssayBuilder:
        """Creates an AssayBuilder that can be used to configure and create
        Assays.
        :param assay_name str: Human friendly name for the assay
        :param pipeline Pipeline: The pipeline this assay will work on
        :param model_name str: The model that this assay will monitor
        :param baseline_start datetime: The start time for the inferences to
            use as the baseline
        :param baseline_end datetime: The end time of the baseline window.
        the baseline. Windows start immediately after the baseline window and
        are run at regular intervals continously until the assay is deactivated
        or deleted.
        """
        assay_builder = AssayBuilder(
            self,
            assay_name,
            pipeline.id(),
            pipeline.name(),
            model_name,
            baseline_start,
            baseline_end,
            iopath="output dense_2 0" if is_arrow_enabled() else "output 0 0",
        )

        return assay_builder

    def upload_assay(self, config: AssayConfig) -> int:
        """Creates an assay in the database.
        :param config AssayConfig: The configuration for the assay to create.
        :return assay_id: The identifier for the assay that was created.
        :rtype int
        """
        data = assays_create.sync(
            client=self.mlops(),
            json_body=AssaysCreateJsonBody.from_dict(
                {
                    **json.loads(config.to_json()),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ),
        )

        if data is None:
            raise Exception("Failed to create assay")

        if not isinstance(data, AssaysCreateResponse200):
            raise Exception(data.msg)

        return data.assay_id

    def list_assays(self) -> List[Assay]:
        """List all assays on the platform.

        :return: A list of all assays on the platform.
        :rtype: List[Assay]
        """
        res = assays_list.sync(client=self.mlops(), json_body=AssaysListJsonBody(UNSET))

        if res is None:
            raise Exception("Failed to get assays")

        if not isinstance(res, List):
            raise Exception(res.msg)

        return Assays([Assay(client=self, data=v.to_dict()) for v in res])

    def create_tag(self, tag_text: str) -> Tag:
        """Create a new tag with the given text."""
        assert tag_text is not None
        return Tag._create_tag(client=self, tag_text=tag_text)

    def create_workspace(self, workspace_name: str) -> Workspace:
        """Create a new workspace with the current user as its first owner.

        :param str workspace_name: Name of the workspace, must be composed of ASCII
           alpha-numeric characters plus dash (-)"""
        assert workspace_name is not None
        require_dns_compliance(workspace_name)
        return Workspace._create_workspace(client=self, name=workspace_name)

    def list_workspaces(self) -> List[Workspace]:
        """List all workspaces on the platform which this user has permission see.

        :return: A list of all workspaces on the platform.
        :rtype: List[Workspace]
        """
        res = workspaces_list.sync(
            client=self.mlops(),
            json_body=workspaces_list_json_body.WorkspacesListJsonBody(UNSET),
        )

        if res is None:
            raise Exception("Failed to get workspaces")

        if not isinstance(res, WorkspacesListResponse200):
            raise Exception(res.msg)

        return Workspaces(
            [Workspace(client=self, data=d.to_dict()) for d in res.workspaces]
        )

    def set_current_workspace(self, workspace: Workspace) -> Workspace:
        """Any calls involving pipelines or models will use the given workspace from then on."""
        assert workspace is not None
        if not isinstance(workspace, Workspace):
            raise TypeError("Workspace type was expected")

        self._current_workspace = workspace
        return cast("Workspace", self._current_workspace)

    def get_current_workspace(self) -> Workspace:
        """Return the current workspace.  See also `set_current_workspace`."""
        if self._current_workspace is None:
            # Is there a default? Use that or make one.
            default_ws = Workspace._get_user_default_workspace(self)
            if default_ws is not None:
                self._current_workspace = default_ws
            else:
                self._current_workspace = Workspace._create_user_default_workspace(self)

        return cast("Workspace", self._current_workspace)

    def invite_user(self, email, password=None):
        return User.invite_user(
            email, password, self.auth, self.api_endpoint, self.auth_endpoint
        )

    def get_topic_name(self, pipeline_pk_id: int) -> str:
        return self._post_rest_api(
            "v1/api/plateau/get_topic_name",
            {
                "pipeline_pk_id": pipeline_pk_id,
            },
        ).json()["topic_name"]

    def shim_token(self, token_data: auth.TokenData):
        fetcher = auth._RawTokenFetcher(token_data)
        self.auth = auth._PlatformAuth(fetcher)

    def convert_model(
        self,
        path: Union[str, pathlib.Path],
        source_type: ModelConversionSource,
        conversion_arguments: ModelConversionArguments,
    ) -> Model:
        """
        Given an inbound source model, a model type (xgboost, keras, sklearn), and conversion arguments.
        Convert the model to onnx, and add to available models for a pipeline.

        :param Union[str, pathlib.Path] path: The path to the model to convert, i.e. the source model.
        :param ModelConversionSource source: The origin model type i.e. keras, sklearn or xgboost.
        :param ModelConversionArguments conversion_arguments: A structure representing the arguments for converting a specific model type.
        :return: An instance of the Model being converted to Onnx.
        :raises ModelConversionGenericException: On a generic failure, please contact our support for further assistance.
        :raises ModelConversionFailure: Failure in converting the model type.
        :raises ModelConversionUnsupportedType: Raised when the source type passed is not supported.
        :raises ModelConversionSourceFileNotPresent: Raised when the passed source file does not exist.
        """
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not os.path.exists(path):
            raise ModelConversionSourceFileNotPresent(
                f"The provided source file: {path} can not be found."
            )
        file_handle = open(path, "rb")
        files = [("files", file_handle)]
        base_url = self.api_endpoint
        workspace_id = self.get_current_workspace().id()
        common_headers = {
            "user_id": self.auth.user_id(),
            "user_email": self.auth.user_email(),
            "User-Agent": _user_agent,
        }
        curry_post = partial(
            requests.post,
            auth=self.auth,
            headers=common_headers,
            files=files,
        )
        model_id: Union[int, None] = None

        def _handle_response(http_response) -> int:
            http_response.raise_for_status()
            response_record = http_response.json()
            if response_record is not None and "model_id" in response_record:
                return int(response_record["model_id"])
            else:
                raise ModelConversionFailure("Failed to convert keras model")

        try:
            if source_type == ModelConversionSource.KERAS:
                assert (
                    type(conversion_arguments).__name__
                    == ConvertKerasArguments.__name__
                )
                ## This is not optimal but api-lb(envoy) -> python-api
                ## Gave a 50(3|4|2|0) on several other options
                ## dimensions being of type List[Any]
                ## dimensions being a base64 encoded json array
                ## dimensions being a comma seperated string that was proccessed server side.
                ## This casts the ConvertKerasArguments dict structure to a json string.
                ## Base64 encoding via a utf-8 binary conversion, passed as the url
                ## parameter config. Which is handlded server side.
                data = {
                    **conversion_arguments.to_dict(),
                    "workspace_id": workspace_id,
                }
                params = {
                    "config": base64.b64encode(json.dumps(data).encode("utf-8")).decode(
                        "utf-8"
                    )
                }
                response = curry_post(url=f"{base_url}/v1/convert/keras", params=params)
                model_id = _handle_response(response)
            elif source_type == ModelConversionSource.SKLEARN:
                assert (
                    type(conversion_arguments).__name__
                    == ConvertSKLearnArguments.__name__
                )
                response = curry_post(
                    url=f"{base_url}/v1/convert/sklearn",
                    params={
                        **conversion_arguments.to_dict(),
                        "workspace_id": workspace_id,
                    },
                )
                model_id = _handle_response(response)

            elif source_type == ModelConversionSource.XGBOOST:
                assert (
                    type(conversion_arguments).__name__ == ConvertXGBoostArgs.__name__
                )
                response = curry_post(
                    url=f"{base_url}/v1/convert/xgboost",
                    params={
                        **conversion_arguments.to_dict(),
                        "workspace_id": workspace_id,
                    },
                )
                model_id = _handle_response(response)
            else:
                raise ModelConversionUnsupportedType(
                    f"Unsupported model source type of {source_type} passed."
                )
            if model_id is None:
                raise ModelConversionFailure("Failed to retrieve final model id")
            return Model(self, {"id": model_id})
        except Exception:
            raise ModelConversionGenericException(
                "This model type could not be deployed successfully. Please contact your Wallaroo support team at community@wallaroo.ai"
            )
        finally:
            file_handle.close()

    def list_orchestrations(self):
        """List all Orchestrations in the current workspace.

        :return: A List containing all Orchestrations in the current workspace.
        """
        return Orchestration.list_orchestrations(self)

    def upload_orchestration(
        self,
        bytes_buffer: Optional[bytes] = None,
        path: Optional[str] = None,
        name: Optional[str] = None,
        file_name: Optional[str] = None,
    ):
        """Upload a file to be packaged and used as an Orchestration.

        The uploaded artifact must be a ZIP file which contains:

        * User code. If `main.py` exists, then that will be used as the task entrypoint. Otherwise,
          the first `main.py` found in any subdirectory will be used as the entrypoint.
        * Optional: A standard Python `requirements.txt` for any dependencies to be provided in the
          task environment. The Wallaroo SDK will already be present and should not be mentioned.
          Multiple `requirements.txt` files are not allowed.
        * Optional: Any other artifacts desired for runtime, including data or code.

        :param Optional[str] path: The path to the file on your filesystem that will be uploaded as an Orchestration.
        :param Optional[bytes] bytes_buffer: The raw bytes to upload to be used Orchestration. Cannot be used with the `path` param.
        :param Optional[str] name: An optional descriptive name for this Orchestration.
        :param Optional[str] file_name: An optional filename to describe your Orchestration when using the bytes_buffer param. Ignored when `path` is used.
        :return: The Orchestration that was uploaded.
        :raises OrchestrationUploadFailed If a server-side error prevented the upload from succeeding.

        """
        return Orchestration.upload(
            self, bytes_buffer=bytes_buffer, path=path, name=name, file_name=file_name
        )

    def list_tasks(self):
        """List all Tasks in the current Workspace.

        :return: A List containing Task objects."""
        return Task.list_tasks(self, self.get_current_workspace().id())

    def in_task(self) -> bool:
        """Determines if this code is inside an orchestration task.

        :return: True if running in a task."""
        return self._in_task

    def task_args(self) -> Dict[Any, Any]:
        """When running inside a task (see `in_task()`), obtain arguments passed to the task.

        :return: Dict of the arguments"""
        with open(self._task_args_filename, "rb") as fp:
            return json.load(fp)

    def list_connections(self) -> ConnectionList:
        """List all Connections defined in the platform.
        :return: List of Connections in the whole platform.
        """
        return Connection.list_connections(self)

    def get_connection(self, name=str) -> Connection:
        """Retrieves a Connection by its name.
        :return: Connection to an external data source.
        """
        return Connection.get_connection(self, name=name)

    def create_connection(
        self, name=str, connection_type=str, details=Dict[str, Any]
    ) -> Connection:
        """Creates a Connection with the given name, type, and type-specific details.
        :return: Connection to an external data source.
        """
        return Connection.create_connection(
            self, name=name, connection_type=connection_type, details=details
        )

    def _post_rest_api_json(self, uri: str, body: dict):
        result = self._post_rest_api(uri, body)
        if result.status_code == 200:
            return result.json()
        else:
            raise Exception(f"{result.status_code}: {result.text}")

    def _setup_mlops_client(self) -> "AuthenticatedClient":
        self._mlops = AuthenticatedClient(
            base_url=self.api_endpoint, token=self.auth._access_token().token
        )
        return self._mlops

    def mlops(self) -> "AuthenticatedClient":
        return self._setup_mlops_client()
