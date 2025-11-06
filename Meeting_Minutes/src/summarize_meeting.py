"""Meeting Summarization Script

Contains functions to parse attendance report & summarize meeting transcripts
"""

import re
from typing import List, Tuple

from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import MetadataMode, TextNode
from loguru import logger

from src.utils.llama_utils import summarize_chunks
from src.utils.prompts import TRANSCRIPT_SUMMARY_QUERY

# Regex pattern to match the start time from attendance.csv summary
START_TIME_PATTERN = re.compile(r'Start time\s+"([^"]+)"')
BOLD_TAG = "**"


def extract_start_date(summary: str) -> str:
    """
    Extracts the start date from a given meeting summary string.

    Args:
        summary (str): A string containing the summary of the meeting,
            including various details.

    Returns:
        The extracted start time in the format found within the
        summary if available, otherwise None.
    """

    # Search for the pattern in the summary
    matches = re.findall(START_TIME_PATTERN, summary)

    # If multiple matches or no match is found, raise an error with more details
    if not matches:
        logger.warning("Start time not found in the summary.")
        return ""
    elif len(matches) > 1:
        logger.warning("Multiple start times found in the summary. Expected only one.")

    # Extract the matched start time
    try:
        start_date = matches[0].split(",")[0]
    except Exception as exp:
        logger.warning(exp)
        return ""

    return start_date


def summarize_meeting(
    nodes: List[TextNode],
    meeting_summarizer: TreeSummarize,
    prompt: str = TRANSCRIPT_SUMMARY_QUERY,
) -> str:
    """Summarize meetings

    Args:
        nodes (TextNode): list of Nodes processed from a vtt file
        prompt (str, optional): Optional Summarize prompt query passed through UI. Defaults to TRANSCRIPT_SUMMARY_QUERY.

    Returns:
        str: Minutes / Summary report of the meeting
    """
    text_chunks = [node.get_content(metadata_mode=MetadataMode.LLM) for node in nodes]
    try:
        transcript_summary = summarize_chunks(
            text_chunks, meeting_summarizer, query=prompt or TRANSCRIPT_SUMMARY_QUERY
        )
    except Exception as exp:
        logger.error(f"Summarizing meeting failed with exception: {exp}")
        raise exp

    return str(transcript_summary)
