# mypy: disable-error-code = misc
from typer import echo
from typer import Exit
from typer import Typer

from visual_novel_toolkit.events.exceptions import EventError
from visual_novel_toolkit.events.plot import plot_events


events = Typer()


@events.command()
def plot() -> None:
    try:
        if plot_events():
            raise Exit(code=1)
    except EventError as error:
        echo(error)
        raise Exit(code=1)
