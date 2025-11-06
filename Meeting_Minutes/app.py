"""FastAPI application for summarizing meeting minutes and documents.

This application provides endpoints for:
- Checking application status
- Summarizing uploaded files with optional custom prompts
- Summarizing meeting minutes with specialized templates

The app uses LLM-based summarization with configurable prompts and templates.
"""

from time import time

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.doc_ingest import process_files
from src.summarize_files import summarize_file
from src.summarize_meeting import summarize_meeting
from src.utils.file_utils import delete_tempfile, write_tempfile
from src.utils.llama_utils import get_summarizer
from src.utils.prompts import (
    get_generic_summarize_template,
    get_meeting_summarize_template,
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Check if the application is running."""
    return {"message": "Status: Running"}


@app.post("/summarize_file")
def summarize(
    file: UploadFile, user_prompt: str = "", system_prompt: str = ""
) -> JSONResponse:
    """Summarize File API

    Args:
        file (UploadFile): Uploaded file from UI
        system_prompt (str, optional):
            Optional System Prompt to pass to translator. Defaults to "".

    Returns:
        JSONResponse:
            JSON Response containing "file_name" and resultant "summary"
    """
    file_path = write_tempfile(file)
    logger.info(f"Summarizing File. Uploaded: {file.filename}")
    tic = time()
    _, nodes = process_files([file_path])

    # Summarize file
    summarize_tmpl = get_generic_summarize_template(system_prompt)
    summarizer = get_summarizer(summarize_tmpl)
    summary = summarize_file(nodes, summarizer, user_prompt)
    toc = time()
    logger.info(f"No. of Nodes: {len(nodes)}")
    logger.info(f"Summary: {summary}")
    logger.info(f"Characters in file: {sum(len(node.text) for node in nodes)}")
    logger.info(f"Summarization Time: {toc -tic:.2f} s")

    delete_tempfile(file_path)
    return JSONResponse(
        content={
            "file_name": file.filename,
            "summary": summary,
        }
    )


@app.post("/summarize_meeting")
def summarize_session(
    vtt_file: UploadFile,
    prompt: str = "",
    system_prompt: str = "",
) -> JSONResponse:
    """Summarize Meeting API

    Args:
        vtt_file (UploadFile): Uploaded meeting transcript file (.vtt)
        attendance_file (UploadFile): Uploaded attendance report file (.csv)
        user_prompt (str, optional):
            Optional user_prompt to summarize specific sections of minutes.
            (Defaults to "".)
        system_prompt (str, optional):
            Optional system_prompt to summarize minutes.
            (Defaults to "".)

    Returns:
        JSONResponse: JSON Response containing the file names and summaries.
    """
    vtt_path = write_tempfile(vtt_file)

    logger.info(f"Summarizing Meeting. Uploaded files: {vtt_file.filename}")

    try:
        # Ingest the transcript and chunk into nodes
        _, nodes = process_files([vtt_path], node_post_process=False)

        # Summarize transcript
        meeting_summarize_tmpl = get_meeting_summarize_template(system_prompt)
        meeting_summarizer = get_summarizer(meeting_summarize_tmpl)
        meeting_minutes = summarize_meeting(nodes, meeting_summarizer, prompt)
    except Exception as exp:
        meeting_minutes = (
            "Meeting Summarization was aborted due to "
            "OpenAI Rate Limits. Please try again later."
        )
        logger.error(exp)
    finally:
        delete_tempfile(vtt_path)

    logger.info(f"No. of Nodes: {len(nodes)}")
    logger.info(f"Meeting Minutes: {meeting_minutes}")
    logger.info(f"Characters: {sum(len(node.text) for node in nodes)}")

    return JSONResponse(
        content={"vtt_file_name": vtt_file.filename, "minutes": meeting_minutes}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
