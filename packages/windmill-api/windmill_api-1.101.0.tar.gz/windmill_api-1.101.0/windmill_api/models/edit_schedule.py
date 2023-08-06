from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.edit_schedule_args import EditScheduleArgs

T = TypeVar("T", bound="EditSchedule")


@attr.s(auto_attribs=True)
class EditSchedule:
    """
    Attributes:
        schedule (str):
        timezone (str):
        args (EditScheduleArgs):
    """

    schedule: str
    timezone: str
    args: EditScheduleArgs
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        schedule = self.schedule
        timezone = self.timezone
        args = self.args.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedule": schedule,
                "timezone": timezone,
                "args": args,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        schedule = d.pop("schedule")

        timezone = d.pop("timezone")

        args = EditScheduleArgs.from_dict(d.pop("args"))

        edit_schedule = cls(
            schedule=schedule,
            timezone=timezone,
            args=args,
        )

        edit_schedule.additional_properties = d
        return edit_schedule

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
