import React, { useEffect, useRef, useState } from "react";
import {
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import SendIcon from "@mui/icons-material/Send";
import {
  StyledContainer,
  MessageContainer,
  Message,
  FileUploadSection,
} from "../RAGChatbot/RAGChatbot.style";

const HRPoliciesChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [error, setError] = useState(""); // Add error state
  const messagesEndRef = useRef(null);

  const baseUrl = process.env.REACT_APP_HR_CHATBOT_ENDPOINT;

  // Add logging when component mounts
  useEffect(() => {
    console.log("HR Chatbot initialized with baseUrl:", baseUrl);
  }, [baseUrl]);

  // Modify session creation with more logging
  useEffect(() => {
    const createSession = async () => {
      try {
        console.log("Creating session at:", `${baseUrl}/api/v1/session`);
        const res = await fetch(`${baseUrl}/api/v1/session`, {
          method: "POST",
        });
        console.log("Session response status:", res.status);

        if (!res.ok) throw new Error("Failed to create session");
        const data = await res.json();
        console.log("Session created successfully:", data);
        setSessionId(data.session_id);
      } catch (e) {
        console.error("Error creating session:", {
          error: e.message,
          baseUrl,
          endpoint: `${baseUrl}/api/v1/session`,
        });
      }
    };
    if (baseUrl) {
      createSession();
    } else {
      console.error("Missing baseUrl for HR Chatbot");
    }
  }, [baseUrl]);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file || !file.type.includes("pdf")) {
      setUploadStatus("Please upload a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/api/v1/upload-pdf`, {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        setUploadStatus("PDF successfully uploaded and processed!");
      } else {
        const text = await response.text();
        setUploadStatus(text || "Error uploading PDF");
      }
    } catch (error) {
      setUploadStatus("Error uploading PDF");
    } finally {
      setLoading(false);
    }
  };

  const handleSendStream = async () => {
    if (!input.trim() || !baseUrl) return;

    console.log("Starting chat request with:", {
      baseUrl,
      sessionId,
      endpoint: `${baseUrl}/api/v1/chat/stream`,
      input,
    });

    // Reset error state
    setError("");

    // Log request details
    console.log("Sending chat request:", {
      sessionId,
      message: input,
      baseUrl,
    });

    // Add message to UI
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      if (!sessionId) {
        console.error("No session ID available");
        throw new Error("No session ID available. Please try refreshing the page.");
      }

      console.log("Sending request to:", `${baseUrl}/api/v1/chat/stream`);
      const response = await fetch(`${baseUrl}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: currentInput,
        }),
      });

      console.log("Stream response:", {
        status: response.status,
        ok: response.ok,
        statusText: response.statusText,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", {
          status: response.status,
          statusText: response.statusText,
          error: errorText,
        });
        throw new Error(
          `API Error: ${response.status} - ${errorText || response.statusText}`
        );
      }

      if (!response.body) {
        throw new Error("Response stream not available");
      }

      // Add assistant message placeholder for UI
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const processChunk = (text) => {
        try {
          buffer += text;
          const parts = buffer.split("\n\n");
          buffer = parts.pop() ?? "";
          for (const part of parts) {
            const lines = part.split("\n");
            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed.startsWith("data:")) continue;
              const payload = trimmed.slice(5).trim();
              if (!payload) continue;

              const json = JSON.parse(payload);
              const delta = json?.content ?? "";
              if (delta) {
                setMessages((prev) => {
                  const next = [...prev];
                  const last = next[next.length - 1];
                  if (last && last.role === "assistant") {
                    last.content = (last.content || "") + delta;
                  }
                  return next;
                });
              }
            }
          }
        } catch (e) {
          console.error("Error processing stream chunk:", e);
          throw e;
        }
      };

      // Read loop
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        processChunk(chunk);
      }

      // flush remaining buffer (if any complete frames without trailing \n\n)
      if (buffer) {
        processChunk("\n\n");
      }
    } catch (err) {
      console.error("Chat error details:", {
        message: err.message,
        baseUrl,
        sessionId,
        input: currentInput,
      });
      setError(err.message || "Failed to get response. Please try again.");
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content:
            "⚠️ " + (err.message || "An error occurred while processing your request."),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledContainer>
      <Typography variant="h4" gutterBottom>
        HR Policies Chatbot
      </Typography>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <FileUploadSection>
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          disabled={loading}
        >
          Upload new HR Policy to Knowledge Base
          <input type="file" hidden accept=".pdf" onChange={handleFileUpload} />
        </Button>
        {uploadStatus && (
          <Typography
            color={uploadStatus.includes("Error") ? "error" : "success"}
          >
            {uploadStatus}
          </Typography>
        )}
      </FileUploadSection>

      <Paper
        elevation={3}
        sx={{
          height: "60vh",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <MessageContainer>
          {messages.map((message, index) => (
            <Message key={index} role={message.role}>
              <Typography>{message.content}</Typography>
            </Message>
          ))}
          <div ref={messagesEndRef} />
        </MessageContainer>

        <Box sx={{ p: 2, borderTop: "1px solid #e0e0e0" }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendStream();
              }
            }}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <Button
                  onClick={handleSendStream}
                  disabled={loading || !input.trim()}
                  sx={{ ml: 1 }}
                >
                  {loading ? <CircularProgress size={24} /> : <SendIcon />}
                </Button>
              ),
            }}
          />
        </Box>
      </Paper>
    </StyledContainer>
  );
};

export default HRPoliciesChatbot;
