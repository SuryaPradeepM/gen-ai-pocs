import React, { useState, useRef, useEffect } from "react";
import {
  Container,
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
} from "./RAGChatbot.style";

console.log(
  "RAG Chatbot Endpoint:",
  process.env.REACT_APP_RAG_CHATBOT_ENDPOINT,
);
console.log("All Environment Variables:", process.env);

const RAGChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.type.includes("pdf")) {
      setUploadStatus("Please upload a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_RAG_CHATBOT_ENDPOINT}/api/v1/upload-pdf`,
        {
          method: "POST",
          body: formData,
        },
      );

      if (response.ok) {
        setUploadStatus("PDF successfully uploaded and processed!");
      } else {
        setUploadStatus("Error uploading PDF");
      }
    } catch (error) {
      setUploadStatus("Error uploading PDF");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_RAG_CHATBOT_ENDPOINT}/api/v1/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [...messages, userMessage],
          }),
        },
      );

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.response },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledContainer>
      <Typography variant="h4" gutterBottom>
        RAG Chatbot
      </Typography>

      <FileUploadSection>
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          disabled={loading}
        >
          Upload PDF
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
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <Button
                  onClick={handleSendMessage}
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

export default RAGChatbot;
