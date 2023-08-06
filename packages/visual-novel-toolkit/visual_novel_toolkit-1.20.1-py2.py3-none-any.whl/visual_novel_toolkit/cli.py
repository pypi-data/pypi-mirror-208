from typer import Typer

from visual_novel_toolkit.drafts.cli import drafts
from visual_novel_toolkit.events.cli import events
from visual_novel_toolkit.speller.cli import speller


cli = Typer()

cli.add_typer(speller, name="speller")
cli.add_typer(drafts, name="drafts")
cli.add_typer(events, name="events")
