# standard libraries
import re
import typing as tp

# third party libraries
import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from spelling_bee_cheat.data_model.puzzle import Puzzle

PUZZLE_URL = "https://www.nytimes.com/puzzles/spelling-bee"
GAME_DATA_RE = re.compile(r"window.gameData\s*=\s*(?P<data>{.*})")
WORDS_POINTS_PANGRAMS_RE = re.compile(r"WORDS: (?P<words>\d+), POINTS: (?P<points>\d+), PANGRAMS: (?P<pangrams>\d+)")


def search_tag(tag: Tag, subtag_type: str, regex: re.Pattern, description: str) -> tp.Tuple[Tag, re.Match]:
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


class TodayAndYesterdayPuzzles(BaseModel):
    """
    Today's puzzle data and yesterday's, just as they are bundled in the page
    data on the NYT spelling bee website.
    """

    today: Puzzle
    yesterday: Puzzle

    @classmethod
    def fetch(cls) -> "TodayAndYesterdayPuzzles":
        """
        Factory method for creating a new TodayAndYesterdayPuzzles instance.
        Fetches the game page from the NYT website, then extracts the puzzle
        data JSON.

        Returns:
            [TodayAndYesterdayPuzzles]: Game data scraped representing puzzles
            from today and yesterday
        """
        # Fetch the webpage that contains today's puzzle.
        r = requests.get(PUZZLE_URL)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract the JSON game data.
        _, mo = search_tag(soup, subtag_type="script", regex=GAME_DATA_RE, description="game data")
        game_data_json = mo.group("data")

        # Construct and return a pydantic representation.
        return cls.parse_raw(game_data_json)


def fetch_hint_text(puzzle: Puzzle) -> str:
    """
    Get hint text from the same day as the provided puzzle. The text giving the
    number of words/points/pangrams is returned. I intend to use this function
    to determine what the cannonically available hints are for spelling bee. I
    want to have the hints be generated from the puzzle data instead of scraping
    them and storing them.

    Args:
        puzzle: puzzle data corresponding to the desired hint data. The
        printDate attribute is used to get the hints from the same date.

    Returns:
        [str]: Text in the same HTML block as the words/points/pangrams counts
    """
    # Fetch the hints webpage.
    date_part = puzzle.printDate.replace("-", "/")
    url = f"https://www.nytimes.com/{date_part}/crosswords/spelling-bee-forum.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # Extract the number of words, points, and pangrams.
    p, _ = search_tag(
        soup,
        subtag_type="p",
        regex=WORDS_POINTS_PANGRAMS_RE,
        description="number of words, points, and pangrams",
    )

    # Return the raw text in the tag.
    return p.text
