from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from typing import NewType


GroupName = NewType("GroupName", str)


EventName = NewType("EventName", str)


ChoiceName = NewType("ChoiceName", str)


IsDecision = NewType("IsDecision", bool)


@dataclass
class Events:
    groups: dict[GroupName, list[EventName]] = field(init=False, default_factory=dict)
    defined: dict[EventName, dict[EventName, ChoiceName | None]] = field(
        init=False, default_factory=dict
    )
    decisions: dict[EventName, IsDecision] = field(init=False, default_factory=dict)
    causes: list[tuple[EventName, EventName]] = field(init=False, default_factory=list)

    @property
    def pairs(self) -> Iterator[tuple[EventName, EventName, ChoiceName | None]]:
        for early, to in self.defined.items():
            for current, choice in to.items():
                yield early, current, choice
