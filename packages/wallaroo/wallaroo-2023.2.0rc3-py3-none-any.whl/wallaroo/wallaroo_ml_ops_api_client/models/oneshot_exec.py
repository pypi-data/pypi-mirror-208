from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.event_base_extra_env_vars import EventBaseExtraEnvVars
  from ..models.oneshot_exec_exec_type import OneshotExecExecType





T = TypeVar("T", bound="OneshotExec")


@attr.s(auto_attribs=True)
class OneshotExec:
    """ 
        Attributes:
            auth_init (bool):
            id (Union[int, str]):
            image (str):
            image_tag (str):
            workspace_id (int):
            flavor (str):
            reap_threshold_secs (int):
            bind_secrets (Union[Unset, List[str]]):
            extra_env_vars (Union[Unset, EventBaseExtraEnvVars]):
            exec_type (Union[Unset, OneshotExecExecType]):
     """

    auth_init: bool
    id: Union[int, str]
    image: str
    image_tag: str
    workspace_id: int
    flavor: str
    reap_threshold_secs: int
    bind_secrets: Union[Unset, List[str]] = UNSET
    extra_env_vars: Union[Unset, 'EventBaseExtraEnvVars'] = UNSET
    exec_type: Union[Unset, 'OneshotExecExecType'] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        auth_init = self.auth_init
        id: Union[int, str]

        id = self.id


        image = self.image
        image_tag = self.image_tag
        workspace_id = self.workspace_id
        flavor = self.flavor
        reap_threshold_secs = self.reap_threshold_secs
        bind_secrets: Union[Unset, List[str]] = UNSET
        if not isinstance(self.bind_secrets, Unset):
            bind_secrets = self.bind_secrets




        extra_env_vars: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.extra_env_vars, Unset):
            extra_env_vars = self.extra_env_vars.to_dict()

        exec_type: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exec_type, Unset):
            exec_type = self.exec_type.to_dict()


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "auth_init": auth_init,
            "id": id,
            "image": image,
            "image_tag": image_tag,
            "workspace_id": workspace_id,
            "flavor": flavor,
            "reap_threshold_secs": reap_threshold_secs,
        })
        if bind_secrets is not UNSET:
            field_dict["bind_secrets"] = bind_secrets
        if extra_env_vars is not UNSET:
            field_dict["extra_env_vars"] = extra_env_vars
        if exec_type is not UNSET:
            field_dict["exec_type"] = exec_type

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.event_base_extra_env_vars import EventBaseExtraEnvVars
        from ..models.oneshot_exec_exec_type import OneshotExecExecType
        d = src_dict.copy()
        auth_init = d.pop("auth_init")

        def _parse_id(data: object) -> Union[int, str]:
            return cast(Union[int, str], data)

        id = _parse_id(d.pop("id"))


        image = d.pop("image")

        image_tag = d.pop("image_tag")

        workspace_id = d.pop("workspace_id")

        flavor = d.pop("flavor")

        reap_threshold_secs = d.pop("reap_threshold_secs")

        bind_secrets = cast(List[str], d.pop("bind_secrets", UNSET))


        _extra_env_vars = d.pop("extra_env_vars", UNSET)
        extra_env_vars: Union[Unset, EventBaseExtraEnvVars]
        if isinstance(_extra_env_vars,  Unset):
            extra_env_vars = UNSET
        else:
            extra_env_vars = EventBaseExtraEnvVars.from_dict(_extra_env_vars)




        _exec_type = d.pop("exec_type", UNSET)
        exec_type: Union[Unset, OneshotExecExecType]
        if isinstance(_exec_type,  Unset):
            exec_type = UNSET
        else:
            exec_type = OneshotExecExecType.from_dict(_exec_type)




        oneshot_exec = cls(
            auth_init=auth_init,
            id=id,
            image=image,
            image_tag=image_tag,
            workspace_id=workspace_id,
            flavor=flavor,
            reap_threshold_secs=reap_threshold_secs,
            bind_secrets=bind_secrets,
            extra_env_vars=extra_env_vars,
            exec_type=exec_type,
        )

        oneshot_exec.additional_properties = d
        return oneshot_exec

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
