from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.v1_model_get_model_by_id_response_200_model_config import \
      V1ModelGetModelByIdResponse200ModelConfig





T = TypeVar("T", bound="V1ModelGetModelByIdResponse200")


@attr.s(auto_attribs=True)
class V1ModelGetModelByIdResponse200:
    """  Response type for /models/get_by_id

        Attributes:
            id (int):  The primary model ID
            owner_id (str):  The user id who created and owns the model.
            name (str):  The name of the model.
            workspace_id (Union[Unset, None, int]):  Workspace Primary id, which the model belongs too.
            updated_at (Union[Unset, None, str]):  When the model was last updated.
            created_at (Union[Unset, None, str]):  When the model was first created.
            model_config (Union[Unset, None, V1ModelGetModelByIdResponse200ModelConfig]):  A possible Model Configuration
     """

    id: int
    owner_id: str
    name: str
    workspace_id: Union[Unset, None, int] = UNSET
    updated_at: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, None, str] = UNSET
    model_config: Union[Unset, None, 'V1ModelGetModelByIdResponse200ModelConfig'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        owner_id = self.owner_id
        name = self.name
        workspace_id = self.workspace_id
        updated_at = self.updated_at
        created_at = self.created_at
        model_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.model_config, Unset):
            model_config = self.model_config.to_dict() if self.model_config else None


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "owner_id": owner_id,
            "name": name,
        })
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if model_config is not UNSET:
            field_dict["model_config"] = model_config

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.v1_model_get_model_by_id_response_200_model_config import \
            V1ModelGetModelByIdResponse200ModelConfig
        d = src_dict.copy()
        id = d.pop("id")

        owner_id = d.pop("owner_id")

        name = d.pop("name")

        workspace_id = d.pop("workspace_id", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        created_at = d.pop("created_at", UNSET)

        _model_config = d.pop("model_config", UNSET)
        model_config: Union[Unset, None, V1ModelGetModelByIdResponse200ModelConfig]
        if _model_config is None:
            model_config = None
        elif isinstance(_model_config,  Unset):
            model_config = UNSET
        else:
            model_config = V1ModelGetModelByIdResponse200ModelConfig.from_dict(_model_config)




        v1_model_get_model_by_id_response_200 = cls(
            id=id,
            owner_id=owner_id,
            name=name,
            workspace_id=workspace_id,
            updated_at=updated_at,
            created_at=created_at,
            model_config=model_config,
        )

        v1_model_get_model_by_id_response_200.additional_properties = d
        return v1_model_get_model_by_id_response_200

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
