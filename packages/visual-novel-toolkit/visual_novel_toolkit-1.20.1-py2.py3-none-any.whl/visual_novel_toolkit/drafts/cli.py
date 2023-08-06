# mypy: disable-error-code = misc
from typer import Exit
from typer import Typer

from visual_novel_toolkit.drafts.missed import find_missed_drafts
from visual_novel_toolkit.drafts.new import make_draft


drafts = Typer()


@drafts.command()
def new() -> None:
    make_draft()


@drafts.command()
def missed() -> None:
    if find_missed_drafts():
        raise Exit(code=1)
