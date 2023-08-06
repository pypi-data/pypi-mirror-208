from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetTaskByIdRequest")


@attr.s(auto_attribs=True)
class GetTaskByIdRequest:
    """ 
        Attributes:
            id (str):
            run_limit (Union[Unset, None, int]):
     """

    id: str
    run_limit: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        run_limit = self.run_limit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })
        if run_limit is not UNSET:
            field_dict["run_limit"] = run_limit

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        run_limit = d.pop("run_limit", UNSET)

        get_task_by_id_request = cls(
            id=id,
            run_limit=run_limit,
        )

        get_task_by_id_request.additional_properties = d
        return get_task_by_id_request

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
