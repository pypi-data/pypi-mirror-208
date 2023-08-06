from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.v1_model_get_config_response_200_model_config import \
      V1ModelGetConfigResponse200ModelConfig





T = TypeVar("T", bound="V1ModelGetConfigResponse200")


@attr.s(auto_attribs=True)
class V1ModelGetConfigResponse200:
    """  Response body of /models/get_config_by_id

        Attributes:
            model_config (Union[Unset, None, V1ModelGetConfigResponse200ModelConfig]):  An optional Model Configuration
     """

    model_config: Union[Unset, None, 'V1ModelGetConfigResponse200ModelConfig'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        model_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.model_config, Unset):
            model_config = self.model_config.to_dict() if self.model_config else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if model_config is not UNSET:
            field_dict["model_config"] = model_config

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.v1_model_get_config_response_200_model_config import \
            V1ModelGetConfigResponse200ModelConfig
        d = src_dict.copy()
        _model_config = d.pop("model_config", UNSET)
        model_config: Union[Unset, None, V1ModelGetConfigResponse200ModelConfig]
        if _model_config is None:
            model_config = None
        elif isinstance(_model_config,  Unset):
            model_config = UNSET
        else:
            model_config = V1ModelGetConfigResponse200ModelConfig.from_dict(_model_config)




        v1_model_get_config_response_200 = cls(
            model_config=model_config,
        )

        v1_model_get_config_response_200.additional_properties = d
        return v1_model_get_config_response_200

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
