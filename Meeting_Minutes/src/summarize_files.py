"""File Summarization Script
"""

from collections import defaultdict
from typing import Dict, List

from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import MetadataMode, TextNode
from loguru import logger

from src.utils.llama_utils import summarize_chunks
from src.utils.prompts import GENERIC_SUMMARY_QUERY


def summarize_file(
    nodes: List[TextNode],
    file_summarizer: TreeSummarize,
    prompt: str = GENERIC_SUMMARY_QUERY,
) -> str:
    """Summarize file

    Args:
        nodes (TextNode): list of Nodes processed from a **single** file
        prompt (str, optional): Optional Summarize prompt query passed through UI. Defaults to GENERIC_SUMMARY_QUERY.

    Returns:
        str: High-level Summary of the file
    """
    text_chunks = [node.get_content(metadata_mode=MetadataMode.LLM) for node in nodes]
    summary = summarize_chunks(
        text_chunks, file_summarizer, query=prompt or GENERIC_SUMMARY_QUERY
    )
    return str(summary)


def summarize_files(
    nodes: List[TextNode],
    file_summarizer: TreeSummarize,
    prompt: str = GENERIC_SUMMARY_QUERY,
) -> Dict[str, str]:
    """Summarize files

    Args:
        nodes (TextNode): list of Nodes processed from **multiple** files (could be from multiple)
        prompt (str, optional): Optional Summarize prompt query passed through UI. Defaults to GENERIC_SUMMARY_QUERY.

    Returns:
        summaries (dict): High-level Summaries of each file in nodes | {file_name: summary_str, ...}
    """
    file_summaries = defaultdict(str)
    file_nodes = defaultdict(list)

    for node in nodes:
        file_nodes[
            (
                node.metadata.get("file_name", None)
                or node.metadata.get("url", None)
                or "Unknown"
            )
        ].append(node)

    logger.debug(f"Summarizing {len(file_nodes)} files")

    for file, nodes in file_nodes.items():
        logger.debug(f"Summarizing: {file}")
        try:
            # TODO: Async Summarization
            file_summaries[file] = summarize_file(nodes, file_summarizer, prompt=prompt)
        except Exception as exp:
            file_summaries[
                file
            ] = "Summarization was aborted due to OpenAI Rate Limits. Please try again later."
            logger.error(f"Summarizing {file} failed with exception: {exp}")

    logger.debug("Successfully summarized all files")
    return dict(file_summaries)
