import React, { useState, useRef } from "react";
import * as speechSdk from "microsoft-cognitiveservices-speech-sdk";

const TextToSpeech = ({ apiKey, region }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [textToRead, setTextToRead] = useState(
    "Hello, this is an announcement.",
  );
  const audioElement = useRef(null); // Ref to control audio playback

  // Function to start speaking
  const playText = () => {
    const speechConfig = speechSdk.SpeechConfig.fromSubscription(
      apiKey,
      region,
    );

    // Disable automatic playback by omitting AudioConfig
    const synthesizer = new speechSdk.SpeechSynthesizer(speechConfig, null);

    synthesizer.speakTextAsync(
      textToRead,
      (result) => {
        if (
          result.reason === speechSdk.ResultReason.SynthesizingAudioCompleted
        ) {
          // When synthesis is complete, retrieve the audio data
          const audioStream = result.audioData;
          const audioBlob = new Blob([audioStream], { type: "audio/wav" });
          const audioUrl = window.URL.createObjectURL(audioBlob);

          // Load the audio into an HTML audio element
          if (audioElement.current) {
            audioElement.current.src = audioUrl;
            audioElement.current.play();
            setIsPlaying(true);

            // Set an event listener to know when the audio has ended
            audioElement.current.onended = () => {
              alert("Audio announcement ended!");
              setIsPlaying(false);
            };
          }
        } else {
          console.error("Speech synthesis failed: ", result.errorDetails);
        }
        synthesizer.close();
      },
      (err) => {
        console.error("Error during speech synthesis: ", err);
        synthesizer.close();
      },
    );
  };

  // Function to pause the speech
  const pauseSpeech = () => {
    if (audioElement.current) {
      audioElement.current.pause();
      setIsPlaying(false);
    }
  };

  return (
    <div>
      <h2>Text to Speech with Azure</h2>
      <textarea
        value={textToRead}
        onChange={(e) => setTextToRead(e.target.value)}
        rows="4"
        cols="50"
      />

      <div>
        {!isPlaying ? (
          <button onClick={playText}>Play</button>
        ) : (
          <button onClick={pauseSpeech}>Pause</button>
        )}
      </div>

      {/* Audio element to handle the playback */}
      <audio ref={audioElement} controls={false} controls />
    </div>
  );
};

export default TextToSpeech;
