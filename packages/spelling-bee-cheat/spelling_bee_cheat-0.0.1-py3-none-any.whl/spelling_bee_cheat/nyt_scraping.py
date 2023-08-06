# standard libraries
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Union

# third party libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag

Pathlike = Union[str, Path]

PUZZLE_URL = "https://www.nytimes.com/puzzles/spelling-bee"
GAME_DATA_RE = re.compile(r"window.gameData\s*=\s*(?P<data>{.*})")
WORDS_POINTS_PANGRAMS_RE = re.compile(r"WORDS: (?P<words>\d+), POINTS: (?P<points>\d+), PANGRAMS: (?P<pangrams>\d+)")
SIGMA_RE = re.compile(r"Σ")
TWO_LETTER_GRID_RE = re.compile(r"([A-Z]{2}-\d+\s*)+")


def search_tag(tag: Tag, subtag_type: str, regex: re.Pattern, description: str) -> Tuple[Tag, re.Match]:
    """
    Search a tag for a subtag containing text matching a regex

    Args:
        tag: root tag to search
        subtag_type: type of tag to look for
        regex: pattern describing the target subtag
        description: description of what is being search for, to be added to
            an exception message if the search fails

    Returns:
        Tag: The first tag containing matching text
        re.Match: the match object from the re library

    Raises:
        RuntimeError: if a matching subtag is not found
    """
    for subtag in tag.find_all(subtag_type):
        mo = regex.search(subtag.text)
        if mo is not None:
            return subtag, mo
    raise RuntimeError(f"Could not find the {subtag_type} tag containing the {description}")


def text_with_br(tag: Tag) -> str:
    """
    Get text from a tag with br tags considered to be newlines. The replacement
    is destructive.

    Args:
        tag: a Tag from BeautifulSoup

    Returns:
        str: text from the tag, with br tags replaced by newlines
    """
    for br in tag.find_all("br"):
        br.replace_with("\n")
    return tag.text


def int_or_id(x: str) -> Union[int, str]:
    """
    Convert a string to int if possible

    Args:
        x: input string

    Returns:
        Union[int, str]: int represented by x, or x itself if parsing fails
    """
    try:
        return int(x)
    except ValueError:
        return x


@dataclass
class HintData:
    """
    Class representing the hints for a spelling bee puzzle
    """

    words: int
    points: int
    pangrams: int

    word_length_grid: pd.DataFrame
    two_letter_grid: pd.DataFrame

    @staticmethod
    def build_word_length_grid(text: str) -> pd.DataFrame:
        """
        Create a dataframe representation of the word length grid from the text
        representation found on the hints page. Output includes the sum column
        and sum row. Dashes are converted to zeros.

        Args:
            text: text from the webpage

        Returns:
            pd.DataFrame: dataframe with letters as index and lengths as columns
        """
        text = text.replace("-", "0")
        lines = text.split("\n")
        header, body = lines[0], lines[1:]

        columns = [int_or_id(x) for x in header.split()]
        index = []
        data = []
        for row in body:
            index_value, data_values = row.split(":")
            index.append(index_value)
            data.append([int(x) for x in data_values.split()])

        return pd.DataFrame(data, columns=columns, index=index)

    @staticmethod
    def build_two_letter_grid(text: str) -> pd.DataFrame:
        """
        Create a dataframe representation of the two letter list from the text
        representation found on the hints page. The representation from the page
        is described as a "two letter list," but this is rearranged into a
        table.

        Args:
            text: text from the webpage

        Returns:
            pd.DataFrame: dataframe with first letters as index and second
                letters as columns
        """
        two_letter_grid = pd.DataFrame()
        for two_letter_hint in text.split():
            letters, number = two_letter_hint.split("-")
            letter1, letter2 = letters
            number = int(number)
            two_letter_grid.loc[letter1, letter2] = number
        two_letter_grid.fillna(0, inplace=True, downcast="infer")
        sorted_columns = sorted(two_letter_grid.columns)
        two_letter_grid = two_letter_grid[sorted_columns]
        return two_letter_grid

    @classmethod
    def fetch_from_date(cls, date: str) -> "HintData":
        """
        Factory for new HintData instance from a date string. Builds a URL,
        fetches the hint page at that URL, and extracts data from it.

        Args:
            date: iso format date string
        """
        # Fetch the hints webpage.
        date_part = date.replace("-", "/")
        url = f"https://www.nytimes.com/{date_part}/crosswords/spelling-bee-forum.html"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract the number of words, points, and pangrams.
        _, mo = search_tag(
            soup,
            subtag_type="p",
            regex=WORDS_POINTS_PANGRAMS_RE,
            description="number of words, points, and pangrams",
        )
        words, points, pangrams = map(int, mo.group("words", "points", "pangrams"))

        # Extract the word length grid.
        p, _ = search_tag(soup, subtag_type="p", regex=SIGMA_RE, description="word length grid")
        p_text = SIGMA_RE.sub(repl="sum", string=text_with_br(p))
        word_length_grid = cls.build_word_length_grid(p_text)

        # Extract the two letter list.
        p, _ = search_tag(
            soup,
            subtag_type="p",
            regex=TWO_LETTER_GRID_RE,
            description="two letter list",
        )
        p_text = text_with_br(p)
        two_letter_grid = cls.build_two_letter_grid(p_text)

        return cls(
            words=words,
            points=points,
            pangrams=pangrams,
            word_length_grid=word_length_grid,
            two_letter_grid=two_letter_grid,
        )


@dataclass
class PuzzleData:
    """
    Class representing a spelling bee puzzle
    """

    game_data_json: str
    game_data: dict

    date: str
    center_letter: str
    outer_letters: List[str]
    valid_letters: List[str]
    pangrams: List[str]
    answers: List[str]
    id_: int

    hint_data: HintData

    @classmethod
    def fetch_today(cls) -> "PuzzleData":
        """
        Factory method for creating a new PuzzleData instance. Fetches the game
        page from the NYT website, then extracts the puzzle data JSON.
        """
        # Fetch the webpage that contains today's puzzle.
        r = requests.get(PUZZLE_URL)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract the game data.
        _, mo = search_tag(soup, subtag_type="script", regex=GAME_DATA_RE, description="game data")
        game_data_json = mo.group("data")
        game_data = json.loads(game_data_json)

        # Extract fields from game data.
        today = game_data["today"]
        date = today["printDate"]
        center_letter = today["centerLetter"]
        outer_letters = today["outerLetters"]
        valid_letters = today["validLetters"]
        pangrams = today["pangrams"]
        answers = today["answers"]
        id_ = today["id"]

        # Use the date from the game data to load the hints.
        hint_data = HintData.fetch_from_date(date)

        return cls(
            game_data_json=game_data_json,
            game_data=game_data,
            date=date,
            center_letter=center_letter,
            outer_letters=outer_letters,
            valid_letters=valid_letters,
            pangrams=pangrams,
            answers=answers,
            id_=id_,
            hint_data=hint_data,
        )
