import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import RecordRTC from "recordrtc";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import {
  Button,
  CircularProgress,
  Typography,
  Box,
  Paper,
  Snackbar,
  Alert,
  IconButton,
} from "@mui/material";
import SimCardDownloadOutlinedIcon from "@mui/icons-material/SimCardDownloadOutlined";
import * as speechSdk from "microsoft-cognitiveservices-speech-sdk"; // Azure Speech SDK import
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import SkipNextIcon from "@mui/icons-material/SkipNext";

const VoiceConversion = ({
  sessionId,
  fileUploaded,
  goToNextSlide,
  totalslides,
}) => {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [presentationStarted, setPresentationStarted] = useState(false);
  const [slideText, setSlideText] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [audioData, setAudioData] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isPermissionDenied, setIsPermissionDenied] = useState(false);
  const mediaRecorderRef = useRef(null);
  const [allTranscripts, setAllTranscripts] = useState([]);
  const {
    transcript: speechTranscript,
    listening,
    resetTranscript,
  } = useSpeechRecognition();
  const scrollRef = useRef(null);
  const timeoutRef = useRef(null);
  const [isPreloading, setIsPreloading] = useState(false);
  const [navFlag, setNavFlag] = useState(true);
  const [audioQueue, setAudioQueue] = useState([]); // To store pre-fetched audio URLs
  const [disableNext, setDisableNext] = useState(true);
  // Load Azure Speech SDK configuration from .env
  const speechConfig = speechSdk.SpeechConfig.fromSubscription(
    process.env.REACT_APP_AZURE_SPEECH_KEY,
    process.env.REACT_APP_AZURE_REGION,
  );

  useEffect(() => {
    scrollToBottom();
  }, [allTranscripts, listening]);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorderRef.current = new RecordRTC(stream, { type: "audio" });
      })
      .catch((error) => {
        console.error("Error accessing microphone:", error);
        setIsPermissionDenied(true);
      });
  }, []);

  useEffect(() => {
    if (listening) {
      resetTimeout();
    }
  }, [listening]);

  useEffect(() => {
    if (speechTranscript) {
      resetTimeout();
    }
  }, [speechTranscript]);

  useEffect(() => {
    if (slideText) {
      const temp = [...allTranscripts, { speaker: "System", text: slideText }];
      setAllTranscripts(temp);
    }
  }, [slideText]);

  useEffect(() => {
    if (audioQueue.length > currentSlide) setDisableNext(false);
    else setDisableNext(true);
  }, [audioQueue, currentSlide]);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  const resetTimeout = () => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (isListening) {
        stopRecordingAndAskQuestion();
      }
    }, 3000);
  };

  const handleExportTranscripts = async () => {
    alert("DOWNLOAD");
    try {
      const response = await axios({
        url: `${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT}/download_transcript/${sessionId}`,
        method: "GET",
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = "transcript.txt";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error downloading the file:", error);
    }
  };

  const fetchAndPlayAudio = async (text) => {
    try {
      const synthesizer = new speechSdk.SpeechSynthesizer(speechConfig, null);

      synthesizer.speakTextAsync(
        text,
        (result) => {
          if (
            result.reason === speechSdk.ResultReason.SynthesizingAudioCompleted
          ) {
            const audioStream = result.audioData; // Retrieve the audio stream
            const audioBlob = new Blob([audioStream], { type: "audio/wav" });
            const audioUrl = window.URL.createObjectURL(audioBlob);

            const temp = audioQueue;
            temp[currentSlide] = { slide: currentSlide, audioUrl, text };
            setAudioQueue([...temp]);

            // Load the audio into an HTML audio element
            setAudioData(audioUrl);
            setIsPlaying(true);
          } else {
            console.error("Speech synthesis failed: ", result.errorDetails);
            setError("Speech synthesis failed.");
          }
          synthesizer.close();
        },
        (err) => {
          console.error("Error during speech synthesis: ", err);
          setError("Error during speech synthesis.");
          synthesizer.close();
        },
      );
    } catch (error) {
      console.error("An error occurred during speech synthesis:", error);
      setError("An error occurred while synthesizing speech.");
    }
  };

  const preloadNextSlideAudio = async (nextSlide) => {
    try {
      setIsPreloading(true);
      const response = await axios.get(
        `${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT}/explain_slide/${sessionId}/${nextSlide}`,
      );
      if (response.status === 200) {
        const text = response.data.explanation;
        const synthesizer = new speechSdk.SpeechSynthesizer(speechConfig, null);

        synthesizer.speakTextAsync(
          text,
          (result) => {
            if (
              result.reason ===
              speechSdk.ResultReason.SynthesizingAudioCompleted
            ) {
              const audioStream = result.audioData;
              const audioBlob = new Blob([audioStream], { type: "audio/wav" });
              const audioUrl = window.URL.createObjectURL(audioBlob);

              // Update the queue with pre-fetched audio
              setAudioQueue((prevQueue) => [
                ...prevQueue,
                { slide: nextSlide, audioUrl, text },
              ]);
              setIsPreloading(false);
            } else {
              console.error("Speech synthesis failed: ", result.errorDetails);
              setError("Speech synthesis failed.");
              setIsPreloading(false);
            }
            synthesizer.close();
          },
          (err) => {
            console.error("Error during speech synthesis: ", err);
            setError("Error during speech synthesis.");
            setIsPreloading(false);
            synthesizer.close();
          },
        );
      }
    } catch (error) {
      console.error("Error preloading slide audio:", error);
      setError("Error preloading slide audio.");
      setIsPreloading(false);
    }
  };

  const handlePrevSlide = () => {
    console.log("current slide>>", currentSlide, audioQueue);
    if (currentSlide >= 2 && currentSlide <= totalslides) {
      let prevSlide = navFlag ? currentSlide - 2 : currentSlide - 1;
      const { audioUrl, text } = audioQueue[prevSlide]; // Play the preloaded audio from the queue
      setUploading(false);
      setSlideText(text);
      setAudioData(audioUrl);
      setIsPlaying(true);
      setCurrentSlide(prevSlide);
      goToNextSlide(prevSlide);
      setNavFlag(false);
    }
  };

  const handlePresentation = async () => {
    // setDisableNext(true)
    setNavFlag(true);
    if (!presentationStarted) {
      setPresentationStarted(true);
    }
    setError(null);
    console.log("audio Queue >>>", audioQueue);
    if (
      (audioQueue?.length > 0 &&
        audioQueue[currentSlide]?.slide === currentSlide &&
        currentSlide >= 1) ||
      audioQueue.length > currentSlide + 1
    ) {
      const { audioUrl, text } = audioQueue[currentSlide]; // Play the preloaded audio from the queue
      setUploading(false);
      setSlideText(text);
      setAudioData(audioUrl);
      setIsPlaying(true);
      setCurrentSlide(currentSlide + 1);
      goToNextSlide(currentSlide);
      preloadNextSlideAudio(currentSlide + 1); // Preload the next slide
    } else {
      // If no preloaded audio, fall back to fetching and playing immediately
      try {
        setUploading(true);
        const response = await axios.get(
          `${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT}/explain_slide/${sessionId}/${currentSlide}`,
        );
        if (response.status === 200) {
          setSlideText(response.data.explanation);
          await fetchAndPlayAudio(response.data.explanation);
          setCurrentSlide(currentSlide + 1);
          goToNextSlide(currentSlide);
          preloadNextSlideAudio(currentSlide + 1); // Preload the next slide
        } else {
          throw new Error(
            `Unexpected response from server: ${response.status}`,
          );
        }
      } catch (error) {
        handleError(error);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleError = (error) => {
    if (error.response) {
      console.error("Server responded with an error:", error.response.data);
    } else if (error.request) {
      console.error("No response received:", error.request);
    } else {
      console.error("Error in setting up request:", error.message);
    }
    setError("An error occurred. Please try again.");
  };

  const startRecording = () => {
    if (isPermissionDenied) {
      setError("Microphone access is denied.");
      return;
    }
    setIsListening(true);
    SpeechRecognition.startListening({
      continuous: true,
      interimResults: true,
    });
    resetTimeout();
  };

  const stopRecordingAndAskQuestion = async () => {
    SpeechRecognition.stopListening();
    setUploading(true);
    setIsListening(false);
    clearTimeout(timeoutRef.current);
    if (speechTranscript) {
      const tempTranscript = speechTranscript;
      const temp = [
        ...allTranscripts,
        { speaker: "You", text: tempTranscript },
      ];
      setAllTranscripts(temp);
      resetTranscript();

      try {
        const response = await axios.post(
          `${process.env.REACT_APP_VIRTUAL_PRESENTER_ENDPOINT}/ask_question/${sessionId}`,
          {
            question: tempTranscript,
          },
        );

        const botTranscript = response.data.answer;
        const temp = [
          ...allTranscripts,
          { speaker: "Presenter", text: botTranscript },
        ];
        setAllTranscripts(temp);
        await fetchAndPlayAudio(botTranscript);
      } catch (error) {
        handleError(error);
      } finally {
        setUploading(false);
      }
    }
  };

  return (
    <Box
      sx={{
        height: "78vh",
        paddingBottom: "40px",
        width: "25%",
        marginTop: "32px",
      }}
    >
      <Paper elevation={3} sx={{ padding: 2 }}>
        {!presentationStarted && (
          <Button
            onClick={handlePresentation}
            variant="contained"
            color="primary"
            sx={{ textTransform: "capitalize" }}
            disabled={
              (presentationStarted && disableNext) ||
              !sessionId ||
              currentSlide > totalslides
            }
          >
            {presentationStarted ? "Next Slide" : "Start Presentation"}
          </Button>
        )}
        <Box sx={{ display: "flex", justifyContent: "space-between" }}>
          {presentationStarted && (
            <Box>
              <IconButton
                onClick={handlePrevSlide}
                disabled={
                  !sessionId || currentSlide > totalslides || currentSlide < 2
                }
                aria-label="previous slide"
                title="previous slide"
              >
                <SkipPreviousIcon />
              </IconButton>
              <Button
                onClick={startRecording}
                variant="contained"
                color={isListening ? "inherit" : "success"}
                sx={{
                  marginLeft: 2,
                  marginRight: 2,
                  textTransform: "capitalize",
                }}
                disabled={
                  isPlaying ||
                  isListening ||
                  !sessionId ||
                  uploading ||
                  (presentationStarted && disableNext)
                }
              >
                {isListening ? "Listening..." : "Ask a Question"}
              </Button>
              <IconButton
                onClick={handlePresentation}
                disabled={
                  disableNext || !sessionId || currentSlide > totalslides
                }
                aria-label="next slide"
                title="next slide"
              >
                <SkipNextIcon />
              </IconButton>
            </Box>
          )}
          {allTranscripts?.length > 0 && (
            <Button
              title="Download Transcripts"
              onClick={handleExportTranscripts}
            >
              <SimCardDownloadOutlinedIcon />
            </Button>
          )}
        </Box>
      </Paper>
      <Box
        ref={scrollRef}
        sx={{
          height: "calc(100% - 50px)",
          overflowY: "auto",
          padding: "16px",
          border: "1px solid #ccc",
          borderRadius: "8px",
          marginTop: "16px",
          marginBottom: "16px",
        }}
      >
        {allTranscripts.map((transcript, index) => (
          <Typography
            key={index}
            variant="body1"
            gutterBottom
            sx={{ fontSize: "14px" }}
          >
            <strong>{transcript.speaker}:</strong> {transcript.text}
          </Typography>
        ))}
        {listening && (
          <Typography variant="body1" gutterBottom>
            <strong>You:</strong> {speechTranscript}
          </Typography>
        )}
        {uploading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <CircularProgress />
          </Box>
        )}
      </Box>
      <audio
        src={audioData}
        controls
        autoPlay
        onEnded={() => {
          setDisableNext(false);
          setIsPlaying(false);
        }}
        onPause={() => setIsPlaying(false)}
      />
      {error && (
        <Snackbar open autoHideDuration={6000} onClose={() => setError(null)}>
          <Alert onClose={() => setError(null)} severity="error">
            {error}
          </Alert>
        </Snackbar>
      )}
    </Box>
  );
};

export default VoiceConversion;
