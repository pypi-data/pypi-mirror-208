from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.create_input_args import CreateInputArgs

T = TypeVar("T", bound="CreateInput")


@attr.s(auto_attribs=True)
class CreateInput:
    """
    Attributes:
        name (str):
        args (CreateInputArgs):
    """

    name: str
    args: CreateInputArgs
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        args = self.args.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "args": args,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        args = CreateInputArgs.from_dict(d.pop("args"))

        create_input = cls(
            name=name,
            args=args,
        )

        create_input.additional_properties = d
        return create_input

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
