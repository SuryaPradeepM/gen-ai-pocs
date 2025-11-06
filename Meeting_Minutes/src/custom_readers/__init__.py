"""Init file - Custom Readers"""

from src.custom_readers.custom_markdown_reader import CustomMarkdownReader
from src.custom_readers.custom_pubmed_reader import CustomPubmedReader
from src.custom_readers.doc_intel_reader import DocIntelReader
from src.custom_readers.simple_pptx_reader import SimplePptxReader
from src.custom_readers.vtt_reader import VttReader
from src.custom_readers.web_reader import CustomTrafilaturaWebReader

__all__ = [
    "CustomMarkdownReader",
    "CustomPubmedReader",
    "DocIntelReader",
    "SimplePptxReader",
    "VttReader",
    "CustomTrafilaturaWebReader",
]
