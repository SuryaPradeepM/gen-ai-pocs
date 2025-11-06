import React, { useEffect, useRef, useState } from 'react';
import { Paper, Typography, TextField, Button, Box, CircularProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SendIcon from '@mui/icons-material/Send';
import { StyledContainer, MessageContainer, Message, FileUploadSection } from '../RAGChatbot/RAGChatbot.style';

const HRPoliciesChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  const baseUrl = process.env.REACT_APP_HR_CHATBOT_ENDPOINT;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const createSession = async () => {
      try {
        const res = await fetch(`${baseUrl}/api/v1/session`, { method: 'POST' });
        if (!res.ok) throw new Error('Failed to create session');
        const data = await res.json();
        setSessionId(data.session_id);
      } catch (e) {
        // keep UI usable even if session fails; retries will happen on next mount/refresh
        // eslint-disable-next-line no-console
        console.error('Error creating session:', e);
      }
    };
    if (baseUrl) {
      createSession();
    }
  }, [baseUrl]);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file || !file.type.includes('pdf')) {
      setUploadStatus('Please upload a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/api/v1/upload-pdf`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        setUploadStatus('PDF successfully uploaded and processed!');
      } else {
        const text = await response.text();
        setUploadStatus(text || 'Error uploading PDF');
      }
    } catch (error) {
      setUploadStatus('Error uploading PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleSendStream = async () => {
    if (!input.trim() || !baseUrl) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${baseUrl}/api/v1/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: currentInput }),
      });

      if (!response.ok || !response.body) {
        throw new Error('Failed to stream response');
      }

      // Insert assistant placeholder message
      let assistantIndex = -1;
      setMessages((prev) => {
        const next = [...prev, { role: 'assistant', content: '' }];
        assistantIndex = next.length - 1;
        return next;
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      const processChunk = (text) => {
        buffer += text;
        const parts = buffer.split('\n\n');
        // keep last partial in buffer
        buffer = parts.pop() ?? '';
        for (const part of parts) {
          const lines = part.split('\n');
          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data:')) continue;
            const payload = trimmed.slice(5).trim();
            if (!payload) continue;
            try {
              const json = JSON.parse(payload);
              const delta = json?.content ?? '';
              if (delta) {
                setMessages((prev) => {
                  const next = [...prev];
                  const last = next[next.length - 1];
                  if (last && last.role === 'assistant') {
                    last.content = (last.content || '') + delta;
                  }
                  return next;
                });
              }
            } catch (e) {
              // eslint-disable-next-line no-console
              console.warn('Bad SSE data:', payload);
            }
          }
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
        processChunk('\n\n');
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Streaming error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <StyledContainer>
      <Typography variant="h4" gutterBottom>
        HR Policies Chatbot
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
          <Typography color={uploadStatus.includes('Error') ? 'error' : 'success'}>
            {uploadStatus}
          </Typography>
        )}
      </FileUploadSection>

      <Paper elevation={3} sx={{ height: '60vh', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <MessageContainer>
          {messages.map((message, index) => (
            <Message key={index} role={message.role}>
              <Typography>{message.content}</Typography>
            </Message>
          ))}
          <div ref={messagesEndRef} />
        </MessageContainer>

        <Box sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendStream();
              }
            }}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <Button onClick={handleSendStream} disabled={loading || !input.trim()} sx={{ ml: 1 }}>
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


