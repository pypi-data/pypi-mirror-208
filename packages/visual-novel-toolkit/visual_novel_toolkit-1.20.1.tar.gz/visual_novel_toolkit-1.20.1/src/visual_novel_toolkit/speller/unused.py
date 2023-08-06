from pathlib import Path
from re import split

from visual_novel_toolkit.speller.dictionaries import dictionaries
from visual_novel_toolkit.speller.words import FileWords


def find_unused_words() -> bool:
    files = (FileWords(dictionary) for dictionary in dictionaries())
    affected = False
    words_cloud = get_words_cloud()
    for json_file in files:
        dictionary = set(json_file.loads())
        unused = dictionary - words_cloud
        if unused:
            json_file.dumps(sorted(dictionary - unused))
            affected = True
    return affected


def get_words_cloud() -> set[str]:
    cloud = set()
    docs = Path("docs")
    for document in docs.glob("**/*.md"):
        words: list[str] = split(r"\W+", document.read_text())
        cloud.update(words)
    return cloud
