# standard libraries
from typing import List

from spelling_bee_cheat.dictionary import load_default_dictionary


def dictionary_search(
    letters: str,
    center_letter: str,
    dictionary: List[str] = None,
) -> List[str]:
    """
    Filter a list of words to those that satisfy the rules of the spelling bee game:
     - contains only letters from the 7 given
     - contains the letter at the center of the puzzle at least once
     - has a minimum length (usually 4)

    Args:
        letters: a string containing the seven allowed letters
        center_letter: a string containing the letter in the center of the puzzle
        dictionary: a list of words to consider. Defaults to nltk.corpus.words.words()

    Returns:
        List[str]: a list of words from the dictionary list that obey the rules of the game
    """
    if dictionary is None:
        dictionary = load_default_dictionary()

    letter_set = set(letters.lower())
    center_letter = center_letter.lower()

    words_found = [word for word in dictionary if center_letter in word and set(word) <= letter_set]

    return words_found
