from pathlib import Path

from visual_novel_toolkit.speller.words import FileWords


def find_duplicated_words() -> bool:
    affected = False
    unique = []
    personal = FileWords(Path("personal.json"))
    wiktionary = FileWords(Path("wiktionary.json")).loads()
    for word in personal.loads():
        if word in wiktionary:
            affected = True
        else:
            unique.append(word)
    if affected:
        personal.dumps(unique)
    return affected
