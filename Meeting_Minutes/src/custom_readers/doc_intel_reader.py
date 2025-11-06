"""Custom Azure AI Document Intelligence parser.

Contains Layout Parser for .pptx, .docx, .pdf and image files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from fsspec import AbstractFileSystem
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from loguru import logger
from tenacity import retry, stop_after_attempt

from src.utils.config_utils import DOTENV_PATH
from src.utils.file_utils import read_file_as_bytes

load_dotenv(DOTENV_PATH)


# https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0#analysis-features
DOC_INTEL_MODEL = "prebuilt-layout"

DOCUMENT_INTELLIGENCE_CLIENT = DocumentIntelligenceClient(
    endpoint=os.environ.get("DOC_INTEL_ENDPOINT"),
    credential=AzureKeyCredential(os.environ.get("DOC_INTEL_KEY")),
    api_version="2024-02-29-preview",
)

RETRY_TIMES = 2


class DocIntelReader(BaseReader):
    """Wrapper over Azure Document Intelligence AI Parser

    Extracts markdown from documents
    Parses Paragraphs, Sections, Sub-sections & Tables
    """

    def __init__(
        self,
        input_files: Optional[List] = None,
        return_full_document: Optional[bool] = False,
    ) -> None:
        """Initialize Reader.

        Args:
            input_files (Optional[List], optional): List of file paths to read. Defaults to None.
            return_full_document (Optional[bool], optional): returns a whole file as a single Document. Defaults to False.
        """
        self.input_files = input_files
        self.return_full_document = return_full_document

    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
    )
    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Loads the file and parses them to return document for each input_file

        Args:
            file (Path): Path to input file
            extra_info (Optional[Dict], optional): A dictionary containing extra metadata information. Defaults to None.
            fs (Optional[fsspec.AbstractFileSystem]): File system to use. Defaults
                to using the local file system. Can be changed to use any remote file system
                exposed via the fsspec interface.
        Returns:
            List[Document]: A list of documents loaded from the input files.
        """
        if not isinstance(file, Path):
            file = Path(file)

        if fs:
            with fs.open(file) as fp:
                file_bytes = read_file_as_bytes(fp)
        else:
            file_bytes = read_file_as_bytes(file)

        result = ""
        documents = []
        poller = DOCUMENT_INTELLIGENCE_CLIENT.begin_analyze_document(
            DOC_INTEL_MODEL,
            AnalyzeDocumentRequest(bytes_source=file_bytes),
            output_content_format="markdown",
        )
        result: AnalyzeResult = poller.result()

        try:
            metadata = {"file_name": file.name}
        except Exception as exp:
            logger.warning(exp)
            metadata = {}
        if extra_info is not None:
            metadata.update(extra_info)

        metadata["content_format"] = "markdown"

        all_pages_content = str(result.content)
        documents.append(Document(text=all_pages_content, metadata=metadata))

        return documents
