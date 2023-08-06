from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.explainability_create_request_json_body_reference_config import \
      ExplainabilityCreateRequestJsonBodyReferenceConfig
  from ..models.explainability_create_request_json_body_window_config import \
      ExplainabilityCreateRequestJsonBodyWindowConfig





T = TypeVar("T", bound="ExplainabilityCreateRequestJsonBody")


@attr.s(auto_attribs=True)
class ExplainabilityCreateRequestJsonBody:
    """  Create a request to be analyzed using a previously created config

        Attributes:
            workspace_id (int):  The users workspace. Must match the workspace of the request and pipelines.
            explainability_config_id (str):  The config to use for this request
            use_adhoc_data (bool):  Specifies if adhoc data should be used. Included because adhoc data is stored in minio.
            id (Union[Unset, None, str]):
            reference_config (Union[Unset, None, ExplainabilityCreateRequestJsonBodyReferenceConfig]):  Specifies if start,
                end and num samples for the reference data.
            window_config (Union[Unset, None, ExplainabilityCreateRequestJsonBodyWindowConfig]):  Specifies if start, end
                and num samples for the a window of data.
            adhoc_data (Union[Unset, None, List[List[float]]]):  User submitted adhoc data.
     """

    workspace_id: int
    explainability_config_id: str
    use_adhoc_data: bool
    id: Union[Unset, None, str] = UNSET
    reference_config: Union[Unset, None, 'ExplainabilityCreateRequestJsonBodyReferenceConfig'] = UNSET
    window_config: Union[Unset, None, 'ExplainabilityCreateRequestJsonBodyWindowConfig'] = UNSET
    adhoc_data: Union[Unset, None, List[List[float]]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        explainability_config_id = self.explainability_config_id
        use_adhoc_data = self.use_adhoc_data
        id = self.id
        reference_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.reference_config, Unset):
            reference_config = self.reference_config.to_dict() if self.reference_config else None

        window_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.window_config, Unset):
            window_config = self.window_config.to_dict() if self.window_config else None

        adhoc_data: Union[Unset, None, List[List[float]]] = UNSET
        if not isinstance(self.adhoc_data, Unset):
            if self.adhoc_data is None:
                adhoc_data = None
            else:
                adhoc_data = []
                for adhoc_data_item_data in self.adhoc_data:
                    adhoc_data_item = adhoc_data_item_data




                    adhoc_data.append(adhoc_data_item)





        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspace_id": workspace_id,
            "explainability_config_id": explainability_config_id,
            "use_adhoc_data": use_adhoc_data,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if reference_config is not UNSET:
            field_dict["reference_config"] = reference_config
        if window_config is not UNSET:
            field_dict["window_config"] = window_config
        if adhoc_data is not UNSET:
            field_dict["adhoc_data"] = adhoc_data

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.explainability_create_request_json_body_reference_config import \
            ExplainabilityCreateRequestJsonBodyReferenceConfig
        from ..models.explainability_create_request_json_body_window_config import \
            ExplainabilityCreateRequestJsonBodyWindowConfig
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        explainability_config_id = d.pop("explainability_config_id")

        use_adhoc_data = d.pop("use_adhoc_data")

        id = d.pop("id", UNSET)

        _reference_config = d.pop("reference_config", UNSET)
        reference_config: Union[Unset, None, ExplainabilityCreateRequestJsonBodyReferenceConfig]
        if _reference_config is None:
            reference_config = None
        elif isinstance(_reference_config,  Unset):
            reference_config = UNSET
        else:
            reference_config = ExplainabilityCreateRequestJsonBodyReferenceConfig.from_dict(_reference_config)




        _window_config = d.pop("window_config", UNSET)
        window_config: Union[Unset, None, ExplainabilityCreateRequestJsonBodyWindowConfig]
        if _window_config is None:
            window_config = None
        elif isinstance(_window_config,  Unset):
            window_config = UNSET
        else:
            window_config = ExplainabilityCreateRequestJsonBodyWindowConfig.from_dict(_window_config)




        adhoc_data = []
        _adhoc_data = d.pop("adhoc_data", UNSET)
        for adhoc_data_item_data in (_adhoc_data or []):
            adhoc_data_item = cast(List[float], adhoc_data_item_data)

            adhoc_data.append(adhoc_data_item)


        explainability_create_request_json_body = cls(
            workspace_id=workspace_id,
            explainability_config_id=explainability_config_id,
            use_adhoc_data=use_adhoc_data,
            id=id,
            reference_config=reference_config,
            window_config=window_config,
            adhoc_data=adhoc_data,
        )

        explainability_create_request_json_body.additional_properties = d
        return explainability_create_request_json_body

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
