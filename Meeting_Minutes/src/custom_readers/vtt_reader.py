"""Custom Transcript parser.

Contains Parser for .vtt (Video Text Tracks format) files.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import webvtt
from fsspec import AbstractFileSystem
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from loguru import logger
from tqdm import tqdm

TEN_SECONDS = timedelta(seconds=10)  # timedelta to gauge pauses in meeting
SPEAKER_TAG = re.compile(r"<v ([^>]+)>")
REPLACE_COMMAS = str.maketrans("", "", ",")


class VttReader(BaseReader):
    """VTT Transcript parser.

    Extracts text, specifies speakers*, returns Document()'s
    """

    def __init__(self, input_files: Optional[List] = None) -> None:
        """Init VTT parser.
        Args:
            input_files (Optional[List], optional): List of file paths to read. Defaults to None.
        """
        self.input_files = input_files

    def _convert_to_datetime(self, timestamp: str, format_string: str = "%H:%M:%S.%f"):
        return datetime.strptime(timestamp, format_string)

    def _pause_time(self, closing: str, opening: str):
        closing = self._convert_to_datetime(closing)
        opening = self._convert_to_datetime(opening)
        return opening - closing

    def _big_pause(self, closing: str, opening: str, time_delta=TEN_SECONDS) -> bool:
        pause_duration = self._pause_time(closing, opening)
        return pause_duration > time_delta

    def _parse_vtt(self, vtt_captions, pause_based_sections: bool = True) -> str:
        """"""
        """Parse VTT transcription file to identify speakers and add sections, where req.

        Args:
            vtt_captions: Loaded vtt_captions
            pause_based_sections (bool, optional): A boolean indicating whether to split the documents into pause-based sections. Defaults to True.

        Returns:
            transcript (str): Parsed, formatted transcript
        """

        transcript = ""
        lines = []
        last_speaker = None
        prev_caption_end = "00:00:00.000"

        for caption in vtt_captions:
            # If extended pauses in captions, add new lines to denote new section
            if pause_based_sections and self._big_pause(
                prev_caption_end, caption.start
            ):
                lines.append("\n\n\n")
            prev_caption_end = caption.end  # update prev end time

            # TODO: P4 | Test, if speaker tag present in other lines
            # TODO: Also, add times of captions in output lines
            first_line = caption.lines[0]
            match = re.match(SPEAKER_TAG, first_line)
            if match:
                speaker = match.group(1).translate(REPLACE_COMMAS)
                if last_speaker != speaker:
                    lines.append("\n\n" + speaker + ": ")
                last_speaker = speaker
            lines.extend(caption.text.strip().splitlines())

        previous = None
        for line in lines:
            if line == previous:
                continue
            transcript += f" {line}"
            previous = line

        logger.debug(f"Length of original:\t{len(vtt_captions.content)} characters")
        logger.debug(f"Length of final:\t{len(transcript)} characters")
        logger.debug(
            f"Percent Reduction:\t{100 - len(transcript)*100/len(vtt_captions.content):.0f}%"
        )

        return transcript

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
        if fs:
            with fs.open(file) as fp:
                vtt_captions = webvtt.read(fp)
        else:
            vtt_captions = webvtt.read(file)

        try:
            metadata = {"file_name": file.name}
        except:
            metadata = {}
        if extra_info is not None:
            metadata.update(extra_info)
        transcript = self._parse_vtt(vtt_captions)
        return [Document(text=transcript, metadata=metadata)]

    def load_files(
        self,
        show_progress: bool = False,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """Loads the vtt_files and parses them to return document for each input_file

        Args:
            show_progress (bool): Whether to show tqdm progress bars. Defaults to False.
            extra_info (Optional[Dict], optional): A dictionary containing extra information. Defaults to None.

        Returns:
            List[Document]: A list of documents loaded from the input files.
        """
        documents = []
        files_to_process = self.input_files
        if show_progress:
            files_to_process = tqdm(
                self.input_files, desc="Loading VTT files", unit="file"
            )
        for input_file in files_to_process:
            documents.append(self.load_data(input_file, extra_info=extra_info))
        return documents
