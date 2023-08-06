from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterator
from functools import reduce
from json import loads
from operator import xor
from pathlib import Path
from re import split
from typing import Final
from typing import TypeAlias
from typing import TypedDict
from typing import TypeVar

from visual_novel_toolkit.speller.dictionaries import dictionaries
from visual_novel_toolkit.speller.words import FileWords
from visual_novel_toolkit.workspace import internal_directory


report_file: Final = internal_directory / "yaspeller_report.json"


def load_mistakes() -> Mistakes:
    if report_file.exists():
        content = report_file.read_text()
        report: Report = loads(content)
    else:
        report = []
    return unfixed(flatten_report(report))


def flatten_report(report: Report) -> Mistakes:
    for each in report:
        resource = Path(each[1]["resource"])
        text = resource_text(resource)
        for item in each[1]["data"]:
            if item["word"] in text:
                yield item["word"], resource, item.get("suggest", [])


def resource_text(resource: Path) -> set[str]:
    if resource.exists():
        words: list[str] = split(r"\W+", resource.read_text())
        return set(words)
    else:
        return set()


def unfixed(flat_report: Mistakes) -> Mistakes:
    files = (FileWords(dictionary) for dictionary in dictionaries())
    init: set[str] = set()
    words = reduce(XOR, (set(dictionary.loads()) for dictionary in files), init)
    for mistake in flat_report:
        if mistake[0] not in words:
            yield mistake


Mistake: TypeAlias = tuple[str, Path, list[str]]


Mistakes = Iterator[Mistake]


class Item(TypedDict):
    word: str
    suggest: list[str]


class Items(TypedDict):
    resource: str
    data: list[Item]


Report: TypeAlias = list[tuple[bool, Items]]


T = TypeVar("T")
XOR: Callable[[T, T], T] = xor
