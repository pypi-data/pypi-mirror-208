from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.new_script_with_draft_draft import NewScriptWithDraftDraft
from ..models.new_script_with_draft_kind import NewScriptWithDraftKind
from ..models.new_script_with_draft_language import NewScriptWithDraftLanguage
from ..models.new_script_with_draft_schema import NewScriptWithDraftSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="NewScriptWithDraft")


@attr.s(auto_attribs=True)
class NewScriptWithDraft:
    """
    Attributes:
        path (str):
        summary (str):
        description (str):
        content (str):
        language (NewScriptWithDraftLanguage):
        hash_ (str):
        parent_hash (Union[Unset, str]):
        schema (Union[Unset, NewScriptWithDraftSchema]):
        is_template (Union[Unset, bool]):
        lock (Union[Unset, List[str]]):
        kind (Union[Unset, NewScriptWithDraftKind]):
        tag (Union[Unset, str]):
        draft_only (Union[Unset, bool]):
        draft (Union[Unset, NewScriptWithDraftDraft]):
    """

    path: str
    summary: str
    description: str
    content: str
    language: NewScriptWithDraftLanguage
    hash_: str
    parent_hash: Union[Unset, str] = UNSET
    schema: Union[Unset, NewScriptWithDraftSchema] = UNSET
    is_template: Union[Unset, bool] = UNSET
    lock: Union[Unset, List[str]] = UNSET
    kind: Union[Unset, NewScriptWithDraftKind] = UNSET
    tag: Union[Unset, str] = UNSET
    draft_only: Union[Unset, bool] = UNSET
    draft: Union[Unset, NewScriptWithDraftDraft] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path
        summary = self.summary
        description = self.description
        content = self.content
        language = self.language.value

        hash_ = self.hash_
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
        draft: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.draft, Unset):
            draft = self.draft.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "summary": summary,
                "description": description,
                "content": content,
                "language": language,
                "hash": hash_,
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
        if draft is not UNSET:
            field_dict["draft"] = draft

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        summary = d.pop("summary")

        description = d.pop("description")

        content = d.pop("content")

        language = NewScriptWithDraftLanguage(d.pop("language"))

        hash_ = d.pop("hash")

        parent_hash = d.pop("parent_hash", UNSET)

        _schema = d.pop("schema", UNSET)
        schema: Union[Unset, NewScriptWithDraftSchema]
        if isinstance(_schema, Unset):
            schema = UNSET
        else:
            schema = NewScriptWithDraftSchema.from_dict(_schema)

        is_template = d.pop("is_template", UNSET)

        lock = cast(List[str], d.pop("lock", UNSET))

        _kind = d.pop("kind", UNSET)
        kind: Union[Unset, NewScriptWithDraftKind]
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = NewScriptWithDraftKind(_kind)

        tag = d.pop("tag", UNSET)

        draft_only = d.pop("draft_only", UNSET)

        _draft = d.pop("draft", UNSET)
        draft: Union[Unset, NewScriptWithDraftDraft]
        if isinstance(_draft, Unset):
            draft = UNSET
        else:
            draft = NewScriptWithDraftDraft.from_dict(_draft)

        new_script_with_draft = cls(
            path=path,
            summary=summary,
            description=description,
            content=content,
            language=language,
            hash_=hash_,
            parent_hash=parent_hash,
            schema=schema,
            is_template=is_template,
            lock=lock,
            kind=kind,
            tag=tag,
            draft_only=draft_only,
            draft=draft,
        )

        new_script_with_draft.additional_properties = d
        return new_script_with_draft

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
