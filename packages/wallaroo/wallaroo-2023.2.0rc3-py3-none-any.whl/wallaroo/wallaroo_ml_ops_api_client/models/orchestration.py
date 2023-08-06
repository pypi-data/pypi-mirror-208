import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.orchestration_status import OrchestrationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Orchestration")


@attr.s(auto_attribs=True)
class Orchestration:
    """ A struct that mirrors the data in Hasura's Orchestration table.

        Attributes:
            created_at (datetime.datetime): When this [Orchestration] was first inserted into the db.
                Optional because they are read-only
            file_name (str): The name of the ZIP archive uploaded by the user. This may be user-provided.
            id (str): The unique identifier for the [Orchestration].
            owner_id (str): This is the UserID of the end user that initiated the upload of this [Orchestration]
            sha (str): The sha256 [String] of the user's uploaded ZIP file.
            status (OrchestrationStatus): The possible states an [Orchestration]'s Packaging status can be in.
            updated_at (datetime.datetime): When this [Orchestration] was last updated in the db.
                Optional because they are read-only
            workspace_id (int): The numeric identifier of the Workspace.
            name (Union[Unset, None, str]): An optional descriptive name provided by the user.
            task_id (Union[None, Unset, int, str]):
     """

    created_at: datetime.datetime
    file_name: str
    id: str
    owner_id: str
    sha: str
    status: OrchestrationStatus
    updated_at: datetime.datetime
    workspace_id: int
    name: Union[Unset, None, str] = UNSET
    task_id: Union[None, Unset, int, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        file_name = self.file_name
        id = self.id
        owner_id = self.owner_id
        sha = self.sha
        status = self.status.value

        updated_at = self.updated_at.isoformat()

        workspace_id = self.workspace_id
        name = self.name
        task_id: Union[None, Unset, int, str]
        if isinstance(self.task_id, Unset):
            task_id = UNSET
        elif self.task_id is None:
            task_id = None

        else:
            task_id = self.task_id



        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "created_at": created_at,
            "file_name": file_name,
            "id": id,
            "owner_id": owner_id,
            "sha": sha,
            "status": status,
            "updated_at": updated_at,
            "workspace_id": workspace_id,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if task_id is not UNSET:
            field_dict["task_id"] = task_id

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))




        file_name = d.pop("file_name")

        id = d.pop("id")

        owner_id = d.pop("owner_id")

        sha = d.pop("sha")

        status = OrchestrationStatus(d.pop("status"))




        updated_at = isoparse(d.pop("updated_at"))




        workspace_id = d.pop("workspace_id")

        name = d.pop("name", UNSET)

        def _parse_task_id(data: object) -> Union[None, Unset, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int, str], data)

        task_id = _parse_task_id(d.pop("task_id", UNSET))


        orchestration = cls(
            created_at=created_at,
            file_name=file_name,
            id=id,
            owner_id=owner_id,
            sha=sha,
            status=status,
            updated_at=updated_at,
            workspace_id=workspace_id,
            name=name,
            task_id=task_id,
        )

        orchestration.additional_properties = d
        return orchestration

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
