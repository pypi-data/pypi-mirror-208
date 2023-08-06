from collections import UserDict
from collections.abc import Iterator
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path

from visual_novel_toolkit.events.data import EventName
from visual_novel_toolkit.events.data import Events
from visual_novel_toolkit.events.load import load


def plot_events() -> bool:
    data = Path("data")
    events_file = data / "events.yml"
    source = events_file.read_text() if events_file.exists() else "{}"

    mermaid = plot(source)

    docs = Path("docs")
    docs.mkdir(exist_ok=True)

    mermaid_file = docs / "events.mmd"
    current = mermaid_file.read_text() if mermaid_file.exists() else ""

    mermaid_file.write_text(mermaid)

    return current != mermaid


def plot(source: str) -> str:
    events = load(source)

    pairs = Pairs(events)

    ids = Lookup()

    lines = ["flowchart BT"]

    for group_name, event_list in events.groups.items():
        lines.append(f"  subgraph {group_name}")
        lines.append("    direction BT")
        lines.extend(plot_event_list(event_list, ids, pairs))
        lines.append("  end")
        lines.append("")

    for left, right, decision in events.pairs:
        sep = f"-- {decision} " if decision is not None else ""
        lines.append(f"  {ids[left]} {sep}--> {ids[right]}")

    for left, right in events.causes:
        lines.append(f"  {ids[left]} -.-> {ids[right]}")

    return "\n".join(lines) + "\n"


class Lookup(UserDict[str, str]):
    def __getitem__(self, item: str) -> str:
        if item in self.data:
            return self.data[item]
        else:
            result = self.data[item] = sha1(item.encode()).hexdigest()
            return result


@dataclass
class Pairs:
    events: Events

    def left(self, event_name: EventName) -> str:
        return "{{" if self.events.decisions[event_name] else "["

    def right(self, event_name: EventName) -> str:
        return "}}" if self.events.decisions[event_name] else "]"


def plot_event_list(
    event_list: list[EventName], ids: Lookup, pairs: Pairs
) -> Iterator[str]:
    for event_name in event_list:
        yield (
            f"    {ids[event_name]}"
            f"{pairs.left(event_name)}"
            f"{event_name}"
            f"{pairs.right(event_name)}"
        )
