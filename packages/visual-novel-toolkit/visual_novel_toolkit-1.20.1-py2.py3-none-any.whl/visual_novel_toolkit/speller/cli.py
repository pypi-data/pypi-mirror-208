# mypy: disable-error-code = misc
from asyncio import run

from typer import echo
from typer import Exit
from typer import Typer

from visual_novel_toolkit.speller.check import check_words
from visual_novel_toolkit.speller.duplicates import find_duplicated_words
from visual_novel_toolkit.speller.exceptions import SpellerError
from visual_novel_toolkit.speller.proofread import proofread_mistakes
from visual_novel_toolkit.speller.review import review_mistakes
from visual_novel_toolkit.speller.sort import sort_words
from visual_novel_toolkit.speller.unused import find_unused_words


speller = Typer()


@speller.command()
def sort() -> None:
    if sort_words():
        raise Exit(code=1)


@speller.command()
def unused() -> None:
    if find_unused_words():
        raise Exit(code=1)


@speller.command()
def duplicates() -> None:
    if find_duplicated_words():
        raise Exit(code=1)


@speller.command()
def proofread() -> None:
    run(proofread_mistakes())


@speller.command()
def review() -> None:
    review_mistakes()


@speller.command()
def check() -> None:
    try:
        if check_words():
            raise Exit(code=1)
    except SpellerError as error:
        echo(error)
        raise Exit(code=1)
