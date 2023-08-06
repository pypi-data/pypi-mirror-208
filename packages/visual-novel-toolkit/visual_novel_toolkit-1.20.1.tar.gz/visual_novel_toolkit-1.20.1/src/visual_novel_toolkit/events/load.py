from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from typing import TypeAlias
from typing import TypedDict

from yaml import CSafeLoader
from yaml import load as _load

from visual_novel_toolkit.events.data import ChoiceName
from visual_novel_toolkit.events.data import EventName
from visual_novel_toolkit.events.data import Events
from visual_novel_toolkit.events.data import GroupName
from visual_novel_toolkit.events.data import IsDecision
from visual_novel_toolkit.events.exceptions import EventError


class Options(TypedDict, total=False):
    decision: ChoiceName
    cause: EventName
    previous: EventName | list[EventName]


Data: TypeAlias = dict[GroupName, list[EventName | dict[EventName, Options]]]


Step: TypeAlias = tuple[
    GroupName,
    EventName,
    list[tuple[EventName, ChoiceName | None]],
    EventName | None,
]


@dataclass
class Traverse:
    data: Data
    last_event: EventName | None = field(init=False)

    def __iter__(self) -> Iterator[Step]:
        for group_name, event_list in self.data.items():
            self.last_event = None
            for event_name in event_list:
                name = self.guess_name(event_name)
                previous = self.guess_previous(name, event_name)
                cause = self.guess_cause(event_name)
                yield group_name, name, previous, cause
                self.last_event = name

    def guess_name(self, event_name: EventName | dict[EventName, Options]) -> EventName:
        if isinstance(event_name, dict):
            return list(event_name.keys())[0]
        elif isinstance(event_name, str):
            return event_name
        else:
            raise RuntimeError

    def guess_previous(
        self, name: EventName, event_name: EventName | dict[EventName, Options]
    ) -> list[tuple[EventName, ChoiceName | None]]:
        options = self.guess_options(event_name)
        previous = self.guess_previous_events(name, options)
        decision = self.guess_decision(options)
        if decision is not None and len(previous) > 1:
            raise EventError(
                "Single decision for multiple previous events found:"
                f" {self.guess_name(event_name)}"
            )
        return [(early, decision) for early in previous]

    def guess_options(
        self, event_name: EventName | dict[EventName, Options]
    ) -> Options:
        if isinstance(event_name, dict):
            return list(event_name.values())[0]
        else:
            return {}

    def guess_previous_events(
        self, name: EventName, options: Options
    ) -> list[EventName]:
        if "previous" not in options:
            return self.guess_last_events()
        elif isinstance(options["previous"], str):
            return [options["previous"]]
        elif isinstance(options["previous"], list):
            check_previous(name, options["previous"])
            return options["previous"]
        else:
            raise RuntimeError

    def guess_last_events(self) -> list[EventName]:
        if self.last_event is not None:
            return [self.last_event]
        else:
            return []

    def guess_decision(self, options: Options) -> ChoiceName | None:
        if "decision" in options:
            return options["decision"]
        else:
            return None

    def guess_cause(
        self, event_name: EventName | dict[EventName, Options]
    ) -> EventName | None:
        options = self.guess_options(event_name)
        if "cause" in options:
            return options["cause"]
        else:
            return None


def check_previous(name: EventName, events: list[EventName]) -> None:
    if len(events) == 1:
        raise EventError(
            f"Multiple previous events syntax used in single previous event: {name}"
        )


def add(events: Events, event_name: EventName, group_name: GroupName) -> None:
    if event_name in events.decisions:
        raise EventError(f"Duplicated event found: {event_name}")
    events.groups.setdefault(group_name, [])
    events.groups[group_name].append(event_name)
    events.decisions[event_name] = IsDecision(False)


def link(
    events: Events,
    event_name: EventName,
    previous: list[tuple[EventName, ChoiceName | None]],
) -> None:
    for early, decision in previous:
        events.decisions[early] = IsDecision(bool(decision))
        events.defined.setdefault(early, {})
        check_decision(events, early, event_name, decision)
        events.defined[early][event_name] = decision


def check_decision(
    events: Events, early: EventName, event_name: EventName, decision: ChoiceName | None
) -> None:
    if decision is None:
        return
    if decision in events.defined[early].values():
        conflict = {v: k for k, v in events.defined[early].items()}[decision]
        raise EventError(
            f"Found duplicated decision {decision!r} from event {early!r} to events "
            f"{conflict!r} and {event_name!r}"
        )


def load(source: str) -> Events:
    data: Data = _load(source, Loader=CSafeLoader)
    traverse = Traverse(data)
    events = Events()

    for group_name, event_name, previous, cause in traverse:
        add(events, event_name, group_name)
        link(events, event_name, previous)
        if cause:
            events.causes.append((cause, event_name))

    return events
