from json import loads
from pathlib import Path
from subprocess import run
from typing import TypedDict

from visual_novel_toolkit.speller.dictionaries import dictionaries
from visual_novel_toolkit.speller.exceptions import SpellerError
from visual_novel_toolkit.workspace import workspace


def check_words() -> bool:
    for conf in [
        ".yaspellerrc",
        ".yaspellerrc.js",
        ".yaspellerrc.json",
        ".yaspeller.json",
    ]:
        if Path(conf).exists():
            raise SpellerError(f"YASpeller configuration file found: {conf}")

    package_file = Path("package.json")
    if package_file.exists():
        package: Package = loads(package_file.read_text())
        if "yaspeller" in package:
            raise SpellerError(f"YASpeller configuration file found: {package_file}")

    args = [
        "--check-yo",
        "--find-repeat-words",
        "--report=console,json",
        "--file-extensions=.md",
        *options(),
    ]

    docs = Path("docs").resolve()

    result = run(["npx", "yaspeller", *args, docs], cwd=workspace())
    return bool(result.returncode)


def options() -> list[str]:
    files = dictionaries()
    if files:
        return [f"--dictionary={':'.join(map(str, files))}"]
    else:
        return []


class Package(TypedDict, total=False):
    yaspeller: dict[str, str]
