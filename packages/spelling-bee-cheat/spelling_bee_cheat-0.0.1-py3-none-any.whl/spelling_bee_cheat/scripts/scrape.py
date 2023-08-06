#!/usr/bin/python
# third party libraries
import click

import spelling_bee_cheat


def report_action_taken(puzzle: spelling_bee_cheat.data_model.Puzzle, existed: bool) -> None:
    """
    Print summary of action taken with given Puzzle

    Args:
        puzzle: puzzle just archived
        existed: return value of the archive operation
    """
    if existed:
        print(f"Puzzle with date {puzzle.printDate} already existed, keeping old version")
    else:
        print("Archived", puzzle.printDate)


@click.command()
@click.option(
    "-d",
    "--archive-dir",
    type=click.Path(exists=True, file_okay=False, writable=True, readable=True),
    default=spelling_bee_cheat.folders.PUZZLE_ARCHIVE_DIR,
)
def scrape(archive_dir: str):
    """
    Download today's and yesterday's spelling bee puzzles from the NYT website
    and save them in JSON files. The file names will contain the publication
    date. They will look like YYYY-MM-DD.json. You can control the archive
    directory with a flag, but the default is the puzzle_archive/ directory in
    the code repo.

    Args:
        archive_dir: folder in which to save the results
    """
    archive = spelling_bee_cheat.archive.Archive(archive_dir)
    tayp, today_existed, yesterday_existed = archive.today_and_yesterday_puzzles(return_existed=True)
    report_action_taken(tayp.today, today_existed)
    report_action_taken(tayp.yesterday, yesterday_existed)


if __name__ == "__main__":
    scrape()
