from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.get_script_by_path_with_draft_response_200_draft_kind import GetScriptByPathWithDraftResponse200DraftKind
from ..models.get_script_by_path_with_draft_response_200_draft_language import (
    GetScriptByPathWithDraftResponse200DraftLanguage,
)
from ..models.get_script_by_path_with_draft_response_200_draft_schema import (
    GetScriptByPathWithDraftResponse200DraftSchema,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetScriptByPathWithDraftResponse200Draft")


@attr.s(auto_attribs=True)
class GetScriptByPathWithDraftResponse200Draft:
    """
    Attributes:
        path (str):
        summary (str):
        description (str):
        content (str):
        language (GetScriptByPathWithDraftResponse200DraftLanguage):
        parent_hash (Union[Unset, str]):
        schema (Union[Unset, GetScriptByPathWithDraftResponse200DraftSchema]):
        is_template (Union[Unset, bool]):
        lock (Union[Unset, List[str]]):
        kind (Union[Unset, GetScriptByPathWithDraftResponse200DraftKind]):
        tag (Union[Unset, str]):
        draft_only (Union[Unset, bool]):
    """

    path: str
    summary: str
    description: str
    content: str
    language: GetScriptByPathWithDraftResponse200DraftLanguage
    parent_hash: Union[Unset, str] = UNSET
    schema: Union[Unset, GetScriptByPathWithDraftResponse200DraftSchema] = UNSET
    is_template: Union[Unset, bool] = UNSET
    lock: Union[Unset, List[str]] = UNSET
    kind: Union[Unset, GetScriptByPathWithDraftResponse200DraftKind] = UNSET
    tag: Union[Unset, str] = UNSET
    draft_only: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        summary = self.summary
        description = self.description
        content = self.content
        language = self.language.value

        parent_hash = self.parent_hash
        schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        is_template = self.is_template
        lock: Union[Unset, List[str]] = UNSET
        if not isinstance(self.lock, Unset):
            lock = self.lock

        kind: Union[Unset, str] = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind.value

        tag = self.tag
        draft_only = self.draft_only

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "summary": summary,
                "description": description,
                "content": content,
                "language": language,
            }
        )
        if parent_hash is not UNSET:
            field_dict["parent_hash"] = parent_hash
        if schema is not UNSET:
            field_dict["schema"] = schema
        if is_template is not UNSET:
            field_dict["is_template"] = is_template
        if lock is not UNSET:
            field_dict["lock"] = lock
        if kind is not UNSET:
            field_dict["kind"] = kind
        if tag is not UNSET:
            field_dict["tag"] = tag
        if draft_only is not UNSET:
            field_dict["draft_only"] = draft_only

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        summary = d.pop("summary")

        description = d.pop("description")

        content = d.pop("content")

        language = GetScriptByPathWithDraftResponse200DraftLanguage(d.pop("language"))

        parent_hash = d.pop("parent_hash", UNSET)

        _schema = d.pop("schema", UNSET)
        schema: Union[Unset, GetScriptByPathWithDraftResponse200DraftSchema]
        if isinstance(_schema, Unset):
            schema = UNSET
        else:
            schema = GetScriptByPathWithDraftResponse200DraftSchema.from_dict(_schema)

        is_template = d.pop("is_template", UNSET)

        lock = cast(List[str], d.pop("lock", UNSET))

        _kind = d.pop("kind", UNSET)
        kind: Union[Unset, GetScriptByPathWithDraftResponse200DraftKind]
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = GetScriptByPathWithDraftResponse200DraftKind(_kind)

        tag = d.pop("tag", UNSET)

        draft_only = d.pop("draft_only", UNSET)

        get_script_by_path_with_draft_response_200_draft = cls(
            path=path,
            summary=summary,
            description=description,
            content=content,
            language=language,
            parent_hash=parent_hash,
            schema=schema,
            is_template=is_template,
            lock=lock,
            kind=kind,
            tag=tag,
            draft_only=draft_only,
        )

        get_script_by_path_with_draft_response_200_draft.additional_properties = d
        return get_script_by_path_with_draft_response_200_draft

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
