import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.list_raw_apps_response_200_item_extra_perms import ListRawAppsResponse200ItemExtraPerms
from ..types import UNSET, Unset

T = TypeVar("T", bound="ListRawAppsResponse200Item")


@attr.s(auto_attribs=True)
class ListRawAppsResponse200Item:
    """
    Attributes:
        workspace_id (str):
        path (str):
        summary (str):
        extra_perms (ListRawAppsResponse200ItemExtraPerms):
        version (float):
        edited_at (datetime.datetime):
        starred (Union[Unset, bool]):
    """

    workspace_id: str
    path: str
    summary: str
    extra_perms: ListRawAppsResponse200ItemExtraPerms
    version: float
    edited_at: datetime.datetime
    starred: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        path = self.path
        summary = self.summary
        extra_perms = self.extra_perms.to_dict()

        version = self.version
        edited_at = self.edited_at.isoformat()

        starred = self.starred

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "path": path,
                "summary": summary,
                "extra_perms": extra_perms,
                "version": version,
                "edited_at": edited_at,
            }
        )
        if starred is not UNSET:
            field_dict["starred"] = starred

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workspace_id = d.pop("workspace_id")

        path = d.pop("path")

        summary = d.pop("summary")

        extra_perms = ListRawAppsResponse200ItemExtraPerms.from_dict(d.pop("extra_perms"))

        version = d.pop("version")

        edited_at = isoparse(d.pop("edited_at"))

        starred = d.pop("starred", UNSET)

        list_raw_apps_response_200_item = cls(
            workspace_id=workspace_id,
            path=path,
            summary=summary,
            extra_perms=extra_perms,
            version=version,
            edited_at=edited_at,
            starred=starred,
        )

        list_raw_apps_response_200_item.additional_properties = d
        return list_raw_apps_response_200_item

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
