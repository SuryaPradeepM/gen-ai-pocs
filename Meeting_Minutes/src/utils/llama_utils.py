from typing import List, Tuple

from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import TextNode
from loguru import logger

from src.utils.config_utils import config
from src.utils.models import llm


def create_nodes(inputs: List[Tuple[str, str]]) -> List[TextNode]:
    """Creates nodes out of any list of inputs.
    Example: create_nodes([("Disease Burden - Impact on Daily Living", "Section Content ..."),
                           ("Disease Burden - Impact on Employment", "Section Content 2 ..."),
                           ]) => List of TextNodes

    Args:
        inputs (List[Tuple[str, str]]): List of tuples, each item having a header or content name followed by a str of text for node content

    Returns:
        List[TextNode]: Nodes created from the inputs.
    """
    nodes = []
    for input_header, input_str in inputs:
        try:
            node = TextNode(
                text=str(input_str),
                metadata={"file_name": str(input_header), "category": "section_input"},
            )
            node.excluded_llm_metadata_keys = ["file_name", "category"]
            nodes.append(node)
        except Exception as exp:
            logger.warning(
                f"Creating node failed for input: {input_header}: {input_str} with Exception: {exp}"
            )
    return nodes


def get_summarizer(summary_template) -> TreeSummarize:
    summarizer = TreeSummarize(
        llm=llm,
        summary_template=summary_template,
        use_async=config["use_async"],
        streaming=config["streaming"],
        verbose=config["debug"],
    )
    return summarizer


def summarize_chunks(
    text_chunks: List[str], summarizer: TreeSummarize, query: str | None = None
) -> str:
    """
    Wrapper over Tree Summarizer with custom Summarize Prompt Instructions
    text_chunks: List of strings containing chunks' text
    query: Pass custom summarize query

    --
    summarizer: TreeSummarizer:
    Tree summarize response builder.

    This response builder recursively merges text chunks and summarizes them
    in a bottom-up fashion (i.e. building a tree from leaves to root).

    More concretely, at each recursively step:
    1. we repack the text chunks so that each chunk fills the context window of the LLM
    2. if there is only one chunk, we give the final response
    3. otherwise, we summarize each chunk and recursively summarize the summaries.
    """

    if not isinstance(text_chunks, list) and isinstance(text_chunks, str):
        # in case a single str is passed instead of a list
        text_chunks = [text_chunks]

    summary = summarizer.get_response(query, text_chunks)
    # could do async
    # summary = await summarizer.aget_response(query_str, text_chunks)
    return str(summary)
