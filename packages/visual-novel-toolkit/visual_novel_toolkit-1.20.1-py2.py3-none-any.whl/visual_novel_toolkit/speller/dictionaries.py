from pathlib import Path


def dictionaries() -> list[Path]:
    return [
        dictionary.resolve()
        for dictionary in [Path("personal.json"), Path("wiktionary.json")]
        if dictionary.exists()
    ]
