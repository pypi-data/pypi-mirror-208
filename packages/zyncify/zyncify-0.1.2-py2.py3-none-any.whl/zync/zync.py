"""
This is the main file for the zync package.
"""

import argparse
from __init__ import methods
from setup import (
    AUTHOR_EMAIL,
    NAME,
    DESCRIPTION,
    URL,
    VERSION,
    AUTHOR,
    AUTHOR_EMAIL,
    LICENSE,
)


def main():
    """
    This is the main function for the zync package.
    """

    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--url", action="url", url=URL)
    parser.add_argument("--license", action="license", license=LICENSE)
    parser.add_argument(
        "--author",
        action="author",
        author=f"{AUTHOR} - {AUTHOR_EMAIL}",
    )
    parser.add_argument(
        "--description",
        action="description",
        description=DESCRIPTION,
    )
    parser.add_argument(
        "--help",
        action="help",
        help=f"available methods: {methods}",
    )


if __name__ == "__main__":
    main()
