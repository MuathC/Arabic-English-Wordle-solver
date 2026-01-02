from .english_validation import is_valid_english_word


def __is_english_alphabet(word:str):
    for char in word:
        if not('a'<=char<='z') and not('A'<=char<='Z'):
            return False
    return True

"""Currently there is no robust way to validate arabic words since every open source dictionary is corrupted and
does not have 100% correct words so we can't use these dictionaries as an authorative source"""


def is_valid_word(word:str):
    if __is_english_alphabet(word):
        return is_valid_english_word(word)
    else:
        return False