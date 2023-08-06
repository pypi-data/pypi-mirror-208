from visual_novel_toolkit.speller.dictionaries import dictionaries
from visual_novel_toolkit.speller.words import FileWords


def sort_words() -> bool:
    files = (FileWords(dictionary) for dictionary in dictionaries())
    affected = False
    for json_file in files:
        dictionary = json_file.loads()
        sorted_dictionary = sorted(set(dictionary))
        if dictionary != sorted_dictionary:
            json_file.dumps(sorted_dictionary)
            affected = True
    return affected
