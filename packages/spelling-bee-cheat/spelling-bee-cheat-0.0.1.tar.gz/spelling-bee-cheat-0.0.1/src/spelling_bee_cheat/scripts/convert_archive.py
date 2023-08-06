#!/usr/bin/python
# standard libraries
import pickle

# third party libraries
import click

import spelling_bee_cheat


@click.command()
def convert_archive():
    """
    Convert the pickle files in the archive directory to json
    """
    archive = spelling_bee_cheat.archive.Archive()
    pickle_files = sorted(archive.path.glob("*.pkl"))
    for pf in pickle_files:
        with pf.open("rb") as f:
            puzzle = pickle.load(f)
        tayp = spelling_bee_cheat.scrape.TodayAndYesterdayPuzzles.parse_raw(puzzle.game_data_json)
        archive.archive(tayp.today)
        archive.archive(tayp.yesterday)


def main():
    """
    Main method. Call into click command
    """
    convert_archive()


if __name__ == "__main__":
    main()
