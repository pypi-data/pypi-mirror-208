#!/usr/bin/python
# third party libraries
import click

import spelling_bee_cheat


@click.command()
def markov():
    """
    Download today's spelling bee puzzle from the NYT website and suggest words
    based on a character level Markov model.
    """
    pdat = spelling_bee_cheat.PuzzleData.fetch_today()
    ms = spelling_bee_cheat.markov_search.MarkovSearch()
    words = ms.markov_search(pdat)
    click.echo_via_pager("".join(word + "\n" for word in words))


if __name__ == "__main__":
    markov()
