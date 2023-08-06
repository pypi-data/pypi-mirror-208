from collections.abc import Iterator
from pathlib import Path
from re import escape
from re import search
from re import split
from re import sub

from typer import echo
from typer import Exit
from typer import getchar
from typer import style

from visual_novel_toolkit.speller.mistakes import load_mistakes
from visual_novel_toolkit.speller.words import FileWords


def review_mistakes() -> None:
    for mistake, source, suggestions in load_mistakes():
        echo("")
        echo(highlight(mistake, source.read_text().strip()))
        if suggestions:
            echo("")
            echo("   ".join(f"[{i}] {word}" for i, word in enumerate(suggestions)))
        echo("")
        echo("[i] Insert   [s] Skip   [q] Quit ", nl=False)
        ask_user = True
        while ask_user:
            match getchar():
                case "q":
                    shutdown()
                case "s":
                    ask_user = skip()
                case "i":
                    ask_user = save(mistake)
                case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" as index:
                    ask_user = correct(source, mistake, int(index), suggestions)


def highlight(word: str, source: str) -> str:
    for sentence in sentences(source):
        position = sentence.find(word)
        if position > -1:
            right = position + len(word)
            return sentence[:position] + style(word, bold=True) + sentence[right:]
    # This line can't be reached because `load_mistakes` checks if
    # word is written in the source file before return it from
    # generator. This line can be reached only if someone run `review`
    # command, pause it, edit file manually and continue `review`
    # after that.
    raise RuntimeError


def sentences(source: str) -> Iterator[str]:
    sentence = []
    tokens: list[str] = split(r"\s+", source)
    for token in tokens:
        sentence.append(token)
        if search(r"(\.|\?|!)$", token):
            yield " ".join(sentence)
            sentence.clear()
    if sentence:  # pragma: no branch
        yield " ".join(sentence)


def shutdown() -> None:
    echo("")

    raise Exit(code=0)


def skip() -> bool:
    echo("")

    return False


def save(mistake: str) -> bool:
    echo("")

    file_words = FileWords(Path("personal.json"))
    dictionary = file_words.loads()
    dictionary.append(mistake)
    dictionary.sort()
    file_words.dumps(dictionary)

    return False


def correct(source: Path, mistake: str, index: int, suggestions: list[str]) -> bool:
    if index >= len(suggestions):
        return True
    else:
        echo("")

        pattern = r"\b" + escape(mistake) + r"\b"
        suggestion = suggestions[index]
        fixed = sub(pattern, suggestion, source.read_text())
        source.write_text(fixed)

        return False
