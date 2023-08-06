# standard libraries
import re
import typing as tp
from functools import cache

# third party libraries
import nltk
import pandas as pd

SPELLING_BEE_WORD_RE = re.compile(r"[a-z]{4,}")


class CorpusWordsWrapper:
    """
    Wrapper class for an NLTK corpus that deduplicates words and filters out
    unacceptable words (i.e. too short, or non-ascii characters).
    """

    def __init__(self, corpus: nltk.corpus.CorpusReader):
        """
        Initializer for CorpusWordsWrapper

        Args:
            corpus: the underlying corpus from NLTK
        """
        self.corpus = corpus
        self._words = None

    def words(self) -> tp.Tuple:
        """
        Get words from the corpus. Remove duplicates, words shorter than four
        letters, and words with non-ascii characters.

        Returns:
            Tuple: lowercase, deduplicated, filtered, sorted words
        """
        if self._words is None:
            words_lower = (word.lower() for word in self.corpus.words())
            words_dedup = set(words_lower)
            words_filtered = (word for word in words_dedup if SPELLING_BEE_WORD_RE.fullmatch(word) is not None)
            self._words = tuple(sorted(words_filtered))

        return self._words


CORPUS_NAMES = [
    "brown",
    "gutenberg",
    "inaugural",
    "reuters",
    "webtext",
    "words",
]
CORPORA = {k: CorpusWordsWrapper(getattr(nltk.corpus, k)) for k in CORPUS_NAMES}


@cache
def load_default_dictionary() -> tp.Tuple:
    """
    Load word lists from several NLTK corpora and combine to create a large word
    list.

    Returns:
        Tuple: tuple of all words
    """
    return tuple(sorted(set().union(*(corpus.words() for corpus in CORPORA.values()))))


class DictionaryDataFrameCache:
    """
    Class for caching the results of load_dictionary_dataframe
    """

    dictionary_dataframe: pd.DataFrame = None

    @classmethod
    def load_dictionary_dataframe(cls) -> pd.DataFrame:
        """
        Load word lists from several NLTK corpora and arrange in a dataframe that
        tracks which words are in which corpora.

        Returns:
            pandas.DataFrame: words as indicies, boolean column for each corpus
        """
        if cls.dictionary_dataframe is None:
            cls.dictionary_dataframe = cls._load_dictionary_dataframe()

        # defensive copy because DataFrames are mutable
        return cls.dictionary_dataframe.copy()

    @classmethod
    def _load_dictionary_dataframe(cls) -> pd.DataFrame:
        df = pd.DataFrame(index=load_default_dictionary())

        for corpus_name, corpus in CORPORA.items():
            df[corpus_name] = False
            df[corpus_name][list(corpus.words())] = True

        return df


load_dictionary_dataframe = DictionaryDataFrameCache.load_dictionary_dataframe
