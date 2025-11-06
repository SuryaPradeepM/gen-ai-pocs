"""Ingest Documents Script

Contains functions to load multiple file types, load to documents,
split to nodes, and, optionally, post-process nodes to extract metadata
"""

import sys

sys.path.append("core")

from pathlib import Path
from typing import List, Optional, Tuple

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import Document, MetadataMode, TextNode
from loguru import logger

from src.custom_extractors.extractors import extract_metadata
from src.custom_readers import (
    CustomMarkdownReader,
    CustomTrafilaturaWebReader,
    DocIntelReader,
    SimplePptxReader,
    VttReader,
)
from src.utils.config_utils import config
from src.utils.models import (
    SPLITTING_STRATEGIES,
    get_splitter,
    markdown_splitter,
    sentence_splitter,
)

SHOW_PROGRESS = config["show_progress"]
SIMPLE_PPT_READER = config["simple_ppt_reader"]
CHUNK_SIZE = config["chunk_size"]
DOC_INTEL_READER = config["doc_intel_reader"]
VTT_READER = config["vtt_reader"]
PPT_EXTENSIONS = {".pptx", ".ppt", ".pptm"}
ENABLE_POST_PROCESSING = config["enable_post_processing"]

# TODO: Can make these singletons
vtt_reader = VttReader()
simple_ptt_reader = SimplePptxReader()
doc_intel_reader = DocIntelReader()
trafilatura_web_reader = CustomTrafilaturaWebReader()
md_reader = CustomMarkdownReader()


def load_files(
    input_paths: List[Path],
    splitting_strategy: str | None = None,
) -> List[Document]:
    """Loads input files"""

    if not isinstance(input_paths, list):
        # In case a single path is passed
        input_paths = [input_paths]

    input_files = []
    for path in input_paths:
        if path.is_dir():
            logger.warning(
                f"Passed a directory instead of a path to a supported file. Excluding Path: {path}"
            )
            continue
        input_files.append(path)

    custom_file_readers = {".md": md_reader}
    if VTT_READER:
        custom_file_readers.update({".vtt": vtt_reader})
    if SIMPLE_PPT_READER:
        custom_file_readers.update(
            {
                ".pptx": simple_ptt_reader,
                ".ppt": simple_ptt_reader,
                ".pptm": simple_ptt_reader,
            }
        )
    if (
        splitting_strategy == "Doc Intelligence + Layout Aware Splitter"
        and DOC_INTEL_READER
    ):
        custom_file_readers.update(
            {
                ".pdf": doc_intel_reader,
                ".docx": doc_intel_reader,
                ".jpg": doc_intel_reader,
                ".png": doc_intel_reader,
                ".jpeg": doc_intel_reader,
            }
        )

    # Load files through SimpleDirectorReader & custom_file_readers
    doc_loader = SimpleDirectoryReader(
        input_files=input_files, file_extractor=custom_file_readers
    )

    return doc_loader.load_data(
        show_progress=SHOW_PROGRESS, num_workers=None  # config["num_workers"]
    )


def load_urls(
    urls: List[str] | None = None,
) -> List[Document]:
    """Loads urls"""
    try:
        url_docs = trafilatura_web_reader.load_data(
            urls=urls,
            output_format="markdown",  # has to "markdown" for sites with complex elements
            include_comments=True,
            include_tables=True,
            include_images=False,
            include_formatting=True,
            include_links=False,
            show_progress=SHOW_PROGRESS,
        )
        return url_docs
    except Exception as exp:
        logger.warning(f"Couldn't load urls: {urls} with Exception: {exp}")
        return []


def load(
    input_paths: List[Path] | None = None,
    urls: List[str] | None = None,
    splitting_strategy: str | None = None,
) -> List[Document]:
    """Loads input files & urls
    Returns list of Documents"""

    documents = []
    if input_paths is not None and len(input_paths) != 0:
        documents.extend(load_files(input_paths, splitting_strategy=splitting_strategy))

    if urls is not None and len(urls) != 0:
        documents.extend(load_urls(urls))

    for doc in documents:
        # Exclude some metadata keys from the purview of embedding and llm models
        doc.excluded_embed_metadata_keys = [
            "file_name",
            "file_path",
            "file_type",
            "file_size",
            "creation_date",
            "last_modified_date",
            "last_accessed_date",
            "page_label",
        ]
        doc.excluded_llm_metadata_keys = [
            "file_name",
            "file_path",
            "file_type",
            "file_size",
            "creation_date",
            "last_modified_date",
            "last_accessed_date",
            "page_label",
        ]
    return documents


def split_documents(
    documents: List[Document], splitting_strategy: str = None
) -> List[TextNode]:
    nodes = list()
    markdown_docs, text_docs = list(), list()

    splitter = get_splitter(splitter_str=splitting_strategy)

    for doc in documents:
        if doc.metadata.get("content_format", "") == "markdown":
            markdown_docs.append(doc)
        else:
            text_docs.append(doc)
    if text_docs:
        for doc in text_docs:
            text_nodes = splitter.get_nodes_from_documents(
                [doc], show_progress=SHOW_PROGRESS
            )
            # Further split the text_nodes if they're beyond the defined chunk_size
            if any(
                len(node.get_content(metadata_mode=MetadataMode.LLM)) >= CHUNK_SIZE
                for node in text_nodes
            ):
                text_nodes = sentence_splitter(text_nodes, show_progress=SHOW_PROGRESS)
            nodes.extend(text_nodes)

    if markdown_docs:
        for doc in markdown_docs:
            md_nodes = markdown_splitter.get_nodes_from_documents(
                [doc], show_progress=SHOW_PROGRESS
            )
            # Further split the md_nodes if they're beyond the defined chunk_size
            if any(
                len(node.get_content(metadata_mode=MetadataMode.LLM)) >= CHUNK_SIZE
                for node in md_nodes
            ):
                md_nodes = sentence_splitter(md_nodes, show_progress=SHOW_PROGRESS)
            nodes.extend(md_nodes)

    return nodes


def process_files(
    input_files: List[Path] | None = None,
    urls: List[str] | None = None,
    labels_descriptions_dict: Optional[dict] = None,
    splitting_strategy: str = None,
    node_post_process: bool = ENABLE_POST_PROCESSING,
    metadata_pipeline: IngestionPipeline = None,
) -> Tuple[List[Document], List[TextNode]]:
    """Given a set of of input_files: (List of paths or single path) to the input documents,
    Loads the documents, splits to nodes and optionally post processes the nodes

    Args:
        input_files (list): List of paths to input files
        urls (List[str], optional): List of URLs to scrape and load nodes. Defaults to None
        labels_descriptions_dict (Optional[dict], optional): TextNode category labels and associated descriptions. Defaults to None.
        splitting_strategy (str, optional): String to select splitting / loading strategy. Defaults to None.
        node_post_process (bool, optional): toggle for node metadata extraction. Defaults to ENABLE_POST_PROCESSING.
        metadata_pipeline (IngestionPipeLine): metadata extraction pipeline to run. Defaults to None. (Only runs if node_post_process is True)

    Returns:
        Tuple[List[Document], List[TextNode]]: List of Document()'s, List of TextNode()'s
    """
    if splitting_strategy not in SPLITTING_STRATEGIES:
        logger.warning(
            f"Splitting strategy: {splitting_strategy} not valid. Pass one of {SPLITTING_STRATEGIES}"
        )
        splitting_strategy = None

    ### Load Documents
    documents = load(
        input_paths=input_files, urls=urls, splitting_strategy=splitting_strategy
    )

    ### Split documents into nodes
    nodes = split_documents(documents, splitting_strategy=splitting_strategy)

    ### Node Post-Process: Metadata Extraction
    if node_post_process:
        extract_metadata(
            nodes,
            labels_descriptions_dict=labels_descriptions_dict,
            pipeline=metadata_pipeline,
        )

    return documents, nodes
