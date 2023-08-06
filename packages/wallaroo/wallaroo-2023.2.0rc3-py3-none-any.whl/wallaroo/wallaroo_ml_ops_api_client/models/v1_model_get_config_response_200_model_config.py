from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.v1_model_get_config_response_200_model_config_tensor_fields import \
      V1ModelGetConfigResponse200ModelConfigTensorFields





T = TypeVar("T", bound="V1ModelGetConfigResponse200ModelConfig")


@attr.s(auto_attribs=True)
class V1ModelGetConfigResponse200ModelConfig:
    """  An optional Model Configuration

        Attributes:
            id (int):  The primary id of the model configuration.
            runtime (str):  The model configuration runtime.
            tensor_fields (Union[Unset, None, V1ModelGetConfigResponse200ModelConfigTensorFields]):  Optional Tensor Fields
                for the model.
            filter_threshold (Union[Unset, None, float]):  An optional filter threshold
     """

    id: int
    runtime: str
    tensor_fields: Union[Unset, None, 'V1ModelGetConfigResponse200ModelConfigTensorFields'] = UNSET
    filter_threshold: Union[Unset, None, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        runtime = self.runtime
        tensor_fields: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.tensor_fields, Unset):
            tensor_fields = self.tensor_fields.to_dict() if self.tensor_fields else None

        filter_threshold = self.filter_threshold

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "runtime": runtime,
        })
        if tensor_fields is not UNSET:
            field_dict["tensor_fields"] = tensor_fields
        if filter_threshold is not UNSET:
            field_dict["filter_threshold"] = filter_threshold

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.v1_model_get_config_response_200_model_config_tensor_fields import \
            V1ModelGetConfigResponse200ModelConfigTensorFields
        d = src_dict.copy()
        id = d.pop("id")

        runtime = d.pop("runtime")

        _tensor_fields = d.pop("tensor_fields", UNSET)
        tensor_fields: Union[Unset, None, V1ModelGetConfigResponse200ModelConfigTensorFields]
        if _tensor_fields is None:
            tensor_fields = None
        elif isinstance(_tensor_fields,  Unset):
            tensor_fields = UNSET
        else:
            tensor_fields = V1ModelGetConfigResponse200ModelConfigTensorFields.from_dict(_tensor_fields)




        filter_threshold = d.pop("filter_threshold", UNSET)

        v1_model_get_config_response_200_model_config = cls(
            id=id,
            runtime=runtime,
            tensor_fields=tensor_fields,
            filter_threshold=filter_threshold,
        )

        v1_model_get_config_response_200_model_config.additional_properties = d
        return v1_model_get_config_response_200_model_config

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
