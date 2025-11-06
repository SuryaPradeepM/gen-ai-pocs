import json
import os
import uuid
import io
import shutil
import logging
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from helper_function import (
    PPTSlideIterator,
    load_llm,
    explain_slide,
    initiate_bot,
    chat,
)
import base64
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
logger = logging.getLogger("AI Presenter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_DIR = "/tmp/session_states"
os.makedirs(SESSION_DIR, exist_ok=True)


class PresentationInit(BaseModel):
    llm_model: str


class QuestionRequest(BaseModel):
    question: str


class ExplanationResponse(BaseModel):
    slide_number: int
    explanation: str


class QuestionResponse(BaseModel):
    answer: str


class TTSRequest(BaseModel):
    text: str


def get_session_file_path(session_id):
    return os.path.join(SESSION_DIR, f"{session_id}.json")


def read_session(session_id):
    file_path = get_session_file_path(session_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Session not found")
    with open(file_path, "r") as f:
        return json.load(f)


def write_session(session_id, data):
    file_path = get_session_file_path(session_id)
    with open(file_path, "w") as f:
        json.dump(data, f)


@app.post("/upload_and_initiate")
async def upload_and_initiate(llm_model: str = "gpt-4-o", file: UploadFile = File(...)):
    try:
        session_id = str(uuid.uuid4())
        os.makedirs(f"presentations/{session_id}", exist_ok=True)
        file_path = f"presentations/{session_id}/{file.filename}"

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        pp = PPTSlideIterator(file_path)
        llm = load_llm(llm_model)
        conversation, convo_history = initiate_bot(pp, llm, [])

        with open(pp.pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # Encode the PDF content to base64
        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        session_data = {
            "pp_path": file_path,
            "llm_model": llm_model,
            "convo_history": [],
            "current_slide": 1,
            "total_slides": pp.get_total_slides(),
        }
        write_session(session_id, session_data)

        return JSONResponse(
            {
                "session_id": session_id,
                "message": "Presentation initialized successfully",
                "total_slides": pp.get_total_slides(),
                "pdf_content": pdf_base64,
            }
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get(
    "/explain_slide/{session_id}/{slide_number}", response_model=ExplanationResponse
)
async def explain_slide_endpoint(session_id: str, slide_number: int):
    session_data = read_session(session_id)
    pp = PPTSlideIterator(session_data["pp_path"])
    llm = load_llm(session_data["llm_model"])

    if slide_number < 1 or slide_number > session_data["total_slides"]:
        raise HTTPException(status_code=400, detail="Invalid slide number")

    explanation = await explain_slide(pp, slide_number, llm)

    session_data["convo_history"].append(
        {"human": f"Explain slide {slide_number}", "ai": explanation}
    )
    session_data["current_slide"] = slide_number
    write_session(session_id, session_data)

    return ExplanationResponse(slide_number=slide_number, explanation=explanation)


@app.post("/ask_question/{session_id}", response_model=QuestionResponse)
async def ask_question(session_id: str, question: QuestionRequest):
    session_data = read_session(session_id)
    pp = PPTSlideIterator(session_data["pp_path"])
    llm = load_llm(session_data["llm_model"])
    conversation, _ = initiate_bot(pp, llm, [])

    response, updated_history = await chat(
        conversation, question.question, session_data["convo_history"]
    )
    session_data["convo_history"] = updated_history
    write_session(session_id, session_data)

    return QuestionResponse(answer=response)


@app.get("/get_current_slide/{session_id}")
async def get_current_slide(session_id: str):
    session_data = read_session(session_id)
    return {"current_slide": session_data["current_slide"]}


@app.get("/total_slides/{session_id}")
async def get_total_slides(session_id: str):
    session_data = read_session(session_id)
    return {"total_slides": session_data["total_slides"]}


@app.get("/download_transcript/{session_id}")
async def download_transcript(session_id: str):
    session_data = read_session(session_id)
    convo_history = session_data.get("convo_history", [])

    transcript = ""
    for entry in convo_history:
        if entry["human"].startswith("Explain slide"):
            transcript += f"--- {entry['human']} ---\n"
            transcript += f"{entry['ai']}\n\n"
        else:
            transcript += f"Question: {entry['human']}\n"
            transcript += f"Answer: {entry['ai']}\n\n"

    if not transcript:
        transcript = "No presentation content or conversation history available."

    buffer = io.StringIO()
    buffer.write(transcript)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=transcript_{session_id}.txt"
        },
    )


@app.get("/get_active_sessions", response_model=List[str])
async def get_session():
    try:
        active_sessions = [
            f.split(".")[0] for f in os.listdir(SESSION_DIR) if f.endswith(".json")
        ]
        return active_sessions
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting active sessions: {str(e)}"
        )


@app.post("/stop_presentation/{session_id}")
async def stop_presentation(session_id: str):
    try:
        session_file = get_session_file_path(session_id)
        if not os.path.exists(session_file):
            raise HTTPException(status_code=404, detail="Session not found")

        os.remove(session_file)

        session_dir = f"presentations/{session_id}"
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)

        return JSONResponse(
            {
                "message": f"Presentation session {session_id} stopped and resources cleaned up successfully"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error stopping presentation: {str(e)}"
        )


@app.post("/clear_all_sessions")
async def clear_all_sessions():
    try:
        # Remove all session files
        for filename in os.listdir(SESSION_DIR):
            if filename.endswith(".json"):
                os.remove(os.path.join(SESSION_DIR, filename))

        # Remove all presentation directories
        presentations_dir = "presentations"
        for session_dir in os.listdir(presentations_dir):
            session_path = os.path.join(presentations_dir, session_dir)
            if os.path.isdir(session_path):
                shutil.rmtree(session_path)

        return JSONResponse(
            {"message": "All sessions cleared and resources cleaned up successfully"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error clearing all sessions: {str(e)}"
        )


@app.post("/text-to-speech/{session_id}")
async def text_to_speech_endpoint(session_id: str, request: TTSRequest):
    try:
        audio_file = await azure_text_to_speech(request.text, session_id)
        return FileResponse(
            audio_file, media_type="audio/mpeg", filename=f"{audio_file.split('/')[-1]}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def azure_text_to_speech(text: str, session_id: str) -> str:
    output_filename = os.path.join(
        SESSION_DIR, f"{session_id}_azure_tts.mp3"
    )  # Use session_id to create a unique filename

    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION"),
    )

    if not speech_config:
        raise Exception(
            "Speech configuration could not be initialized. Check your Azure credentials."
        )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    # Start the synthesis and wait for it to complete
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(
        None, lambda: speech_synthesizer.speak_text_async(text).get()
    )
    result = await future

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return output_filename
    else:
        raise Exception(
            "Speech synthesis failed: Reason: {} Error Details: {}".format(
                result.cancellation_details.reason,
                result.cancellation_details.error_details
                if result.cancellation_details
                else "None",
            )
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
