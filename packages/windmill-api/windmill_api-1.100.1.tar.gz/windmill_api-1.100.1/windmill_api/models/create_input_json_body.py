from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.create_input_json_body_args import CreateInputJsonBodyArgs

T = TypeVar("T", bound="CreateInputJsonBody")


@attr.s(auto_attribs=True)
class CreateInputJsonBody:
    """
    Attributes:
        name (str):
        args (CreateInputJsonBodyArgs):
    """

    name: str
    args: CreateInputJsonBodyArgs
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

        args = CreateInputJsonBodyArgs.from_dict(d.pop("args"))

        create_input_json_body = cls(
            name=name,
            args=args,
        )

        create_input_json_body.additional_properties = d
        return create_input_json_body

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
