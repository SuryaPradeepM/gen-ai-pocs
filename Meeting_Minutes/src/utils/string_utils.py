"""Generic String utils
"""

import io
import re
from typing import List

import pandas as pd
from loguru import logger


def list_to_string(list_of_strings: List[str], sep=",") -> str:
    """
    Convert a list of strings into a single string.
    For converting node metadata category to string to ingest into Azure AI Search

    Returns:
        str: A string that contains all the list elements joined by the separator.
    """
    return sep.join(list_of_strings)


def string_to_list(string: str, sep=",") -> List[str]:
    """
    Convert a string into a list of strings.

    Returns:
        list: A list that contains all the substrings split by the separator.
    """
    return string.split(sep)


def parse_tab_separated_string(input_string: str, header: bool = True) -> pd.DataFrame:
    """Parse a csv string to read to a pandas dataframe

    Args:
        input_string (str): input string loaded from the csv file
        header (bool, optional): If the csv contains a header. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame object loaded from the csv
    """
    # StringIO allows us to treat a string like a file
    string_io = io.StringIO(input_string)

    # Use read_csv function from pandas to parse the tab-separated string
    if header:
        df = pd.read_csv(string_io, delimiter="\t")
    else:
        df = pd.read_csv(string_io, delimiter="\t", header=None)

    return df


def insert_in_string(original_string: str, insert: str, position: int) -> str:
    """Insert a string into original_string at position"""
    try:
        if position < 0 or position > len(original_string):
            return original_string
        else:
            new_string = (
                original_string[:position] + insert + original_string[position:]
            )
            return new_string
    except TypeError:
        return original_string


def find_matches(pattern, test_str: str) -> list:
    """Finds Matches and returns a list of indices of match start and end positions

    Args:
        pattern (_type_): Pattern for finding matches
        test_str (str): String on which matches are to be extracted
    """
    indexes = list()
    matches = re.finditer(pattern, test_str)
    for match_num, match in enumerate(matches, start=1):
        logger.debug(
            "Match {match_num} was found at {start}: {match}".format(
                match_num=match_num, start=match.start(), match=match.group()
            )
        )
        indexes.append(match.end())
        indexes.append(match.start())
    return indexes
