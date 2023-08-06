from json import dumps
from json import loads
from pathlib import Path


class FileWords:
    def __init__(self, path: Path) -> None:
        self.path = path

    def loads(self) -> list[str]:
        if not self.path.exists():
            return []
        else:
            content: list[str] = loads(self.path.read_text())
            return content

    def dumps(self, value: list[str]) -> None:
        content = dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
        self.path.write_text(content + "\n")
