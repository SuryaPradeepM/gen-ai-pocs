import React, { useEffect, useRef, useState } from "react";
import {
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Grid,
} from "@mui/material";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from "@mui/icons-material/Send";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import {
  StyledContainer,
  MessageContainer,
  Message,
  FileUploadSection,
} from "../RAGChatbot/RAGChatbot.style";

// A lightweight DB Genie UI that supports streaming chat and visualizations.
const DBGenie = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [error, setError] = useState("");
  const [tableData, setTableData] = useState(null);
  const [visualization, setVisualization] = useState(null);
  const messagesEndRef = useRef(null);
  const messageContainerRef = useRef(null);
  const [statusMessage, setStatusMessage] = useState("");

  // Clear transient status messages automatically after a few seconds
  useEffect(() => {
    if (!statusMessage) return undefined;
    const t = setTimeout(() => setStatusMessage(""), 6000);
    return () => clearTimeout(t);
  }, [statusMessage]);

  // Auto-scroll chat to the bottom when messages update — only if user is near bottom
  useEffect(() => {
    try {
      const container = messageContainerRef.current;
      if (!container) {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        return;
      }
      const { scrollTop, scrollHeight, clientHeight } = container;
      const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);
      const THRESHOLD = 150; // px - if user is within this distance, auto-scroll
      if (distanceFromBottom < THRESHOLD) {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }
    } catch (e) {
      // ignore in non-browser or unavailable scroll contexts
    }
  }, [messages]);

  const baseUrl = process.env.REACT_APP_DB_GENIE_ENDPOINT;

  useEffect(() => {
    // Create session on mount
    const createSession = async () => {
      if (!baseUrl) {
        console.error("DB Genie baseUrl not configured");
        return;
      }
      try {
        const res = await fetch(`${baseUrl}/api/v1/session`, { method: "POST" });
        if (!res.ok) throw new Error("Failed to create session");
        const data = await res.json();
        setSessionId(data.session_id);
      } catch (e) {
        console.error("Error creating DB Genie session:", e);
      }
    };
    createSession();
  }, [baseUrl]);

  // Helper: pretty-print JSON into messages
  const pushSystemMessage = (text) => {
    setMessages((prev) => [...prev, { role: "system", content: text }]);
  };

  const handleSendStream = async () => {
    if (!input.trim() || !baseUrl) return;
    if (!sessionId) {
      setError("No session. Refresh the page to create a session.");
      return;
    }

    setError("");
    // Add user message
    const currentInput = input;
    setMessages((prev) => [...prev, { role: "user", content: currentInput }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${baseUrl}/api/v1/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: currentInput }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || `API Error ${response.status}`);
      }

      if (!response.body) throw new Error("Response body not available");

      // Add assistant placeholder
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const processChunk = (text) => {
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

            try {
              const json = JSON.parse(payload);

              // Text delta
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

              // visualization or structured data
              if (json.visualization) {
                setVisualization(json.visualization);
              }

              if (json.data) {
                setTableData(json.data);
              }
            } catch (e) {
              console.error("Failed to parse SSE payload", e, payload);
            }
          }
        }
      };

      // Read stream
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        processChunk(chunk);
      }

      // flush
      if (buffer) processChunk("\n\n");
    } catch (err) {
      console.error("DBGenie chat error:", err);
      setError(err.message || "Failed to get response");
      pushSystemMessage("⚠️ " + (err.message || "An error occurred"));
    } finally {
      setLoading(false);
    }
  };

  // Get DB schema
  const fetchSchema = async () => {
    if (!baseUrl) return;
    setLoading(true);
      try {
        const res = await fetch(`${baseUrl}/api/v1/database/schema`);
        if (!res.ok) throw new Error(`Schema API error ${res.status}`);
        const data = await res.json();
        setTableData(data);
        setStatusMessage("Fetched database schema.");
      } catch (e) {
      console.error(e);
      setError(e.message || "Failed to fetch schema");
    } finally {
      setLoading(false);
    }
  };

  // Get sample rows for a table
  const fetchTableSample = async () => {
    const tableName = prompt("Enter table name to fetch a sample (case-sensitive):");
    if (!tableName) return;
    setLoading(true);
    try {
      const res = await fetch(`${baseUrl}/api/v1/database/tables/${encodeURIComponent(tableName)}/sample?limit=5`);
      if (!res.ok) throw new Error(`Sample API error ${res.status}`);
      const data = await res.json();

      // Normalize response shapes from backend so renderTable can consume them.
      // Common backend shapes: { success: true, data: [...] }, { rows: [...] }, { data: [...] }, or directly an array
      let normalized = null;

      if (!data) {
        normalized = null;
      } else if (Array.isArray(data)) {
        normalized = data; // array of rows
      } else if (data.rows && Array.isArray(data.rows)) {
        normalized = { rows: data.rows };
      } else if (data.sample_data && Array.isArray(data.sample_data)) {
        // backend returns sample_data for table samples
        normalized = { rows: data.sample_data };
      } else if (data.data && Array.isArray(data.data)) {
        // some endpoints return { data: [...] }
        normalized = { rows: data.data };
      } else if (data.result && Array.isArray(data.result)) {
        normalized = { rows: data.result };
      } else if (data.success && Array.isArray(data.payload)) {
        normalized = { rows: data.payload };
      } else if (data.success && Array.isArray(data.data)) {
        normalized = { rows: data.data };
      } else {
        // fallback - store raw response so user can inspect
        normalized = data;
      }

      setTableData(normalized);
      setStatusMessage(`Fetched sample for table ${tableName}`);
    } catch (e) {
      console.error(e);
      setError(e.message || "Failed to fetch table sample");
    } finally {
      setLoading(false);
    }
  };

  // Execute raw SQL (read-only checks applied by backend)
  const executeRawSQL = async () => {
    const sql = prompt("Enter SELECT SQL query to execute (must start with SELECT):");
    if (!sql) return;
    setLoading(true);
    try {
      const res = await fetch(`${baseUrl}/api/v1/query/sql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: sql }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || JSON.stringify(data));
      setTableData(data);
      setStatusMessage("SQL query executed. See results below.");
    } catch (e) {
      console.error(e);
      setError(e.message || "Failed to execute SQL");
    } finally {
      setLoading(false);
    }
  };

  // Create visualization from current tableData
  const createVisualization = async () => {
    if (!tableData) {
      setError("No data available to visualize");
      return;
    }
    // Default: send tableData.data or tableData.rows depending on shape
    const payloadData = tableData.data ?? tableData.rows ?? tableData?.schema ?? tableData;

    try {
      setLoading(true);
      const res = await fetch(`${baseUrl}/api/v1/visualize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: payloadData, chart_type: "auto", title: "DBGenie Visualization" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || JSON.stringify(data));
      if (data.visualization) setVisualization(data.visualization);
      if (data.data) setTableData(data.data);
      setStatusMessage("Visualization created.");
    } catch (e) {
      console.error(e);
      setError(e.message || "Failed to create visualization");
    } finally {
      setLoading(false);
    }
  };

  // Small renderer for structured data
  const renderTable = (data) => {
    if (!data) return null;
    // If this is a schema payload, don't try to render it as rows
    if (data.tables && data.schema) return null;
    // If the data contains 'rows' or 'data' or is an array of objects
    const rows = data.rows ?? data.data ?? (Array.isArray(data) ? data : null);
    if (!rows || !rows.length) return <Typography>No tabular data to display</Typography>;

    const cols = Array.from(rows.reduce((acc, r) => {
      Object.keys(r || {}).forEach(k => acc.add(k));
      return acc;
    }, new Set()));

    return (
      <Box sx={{ overflowX: "auto", mt: 2 }}>
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              {cols.map((c) => (
                <th key={c} style={{ border: "1px solid #ddd", padding: 8, textAlign: "left" }}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx}>
                {cols.map((c) => (
                  <td key={c} style={{ border: "1px solid #eee", padding: 8 }}>{String(r[c] ?? "")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    );
  };

  // Summarize DB schema programmatically
  const summarizeSchema = (payload) => {
    if (!payload || !payload.tables || !payload.schema) return null;
    const tables = payload.tables || [];
    const totalTables = tables.length;

    // For each table compute columns count, PKs, FKs
    const perTable = tables.map((t) => {
      const meta = payload.schema[t];
      if (!meta) return { table: t, columns: 0, primary_keys: [], foreign_keys: [] };
      return {
        table: t,
        columns: Object.keys(meta.columns || {}).length,
        primary_keys: meta.primary_keys || [],
        foreign_keys: (meta.foreign_keys || []).map((fk) => ({
          constrained_columns: fk.constrained_columns,
          referred_table: fk.referred_table,
          referred_columns: fk.referred_columns,
        })),
      };
    });

    return { totalTables, tables, perTable };
  };

  const renderSchemaSummary = (payload) => {
    const summary = summarizeSchema(payload);
    if (!summary) return null;

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6">Database Schema (summary)</Typography>
        <Typography sx={{ mt: 1 }}>Total tables: {summary.totalTables}</Typography>
        <Box sx={{ mt: 1 }}>
          {summary.perTable.map((t) => (
            <Paper key={t.table} sx={{ p: 1, mb: 1 }} elevation={1}>
              <Typography variant="subtitle2">{t.table}</Typography>
              <Typography variant="body2">Columns: {t.columns}</Typography>
              <Typography variant="body2">Primary keys: {t.primary_keys.length ? t.primary_keys.join(", ") : "—"}</Typography>
              <Typography variant="body2">Foreign keys: {t.foreign_keys.length ? t.foreign_keys.map(f => `${f.constrained_columns.join(", ")} → ${f.referred_table}(${f.referred_columns.join(", ")})`).join("; ") : "—"}</Typography>
            </Paper>
          ))}
        </Box>

        <Accordion sx={{ mt: 1 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Detailed schema (JSON)</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ maxHeight: 300, overflow: "auto", background: "#f6f6f6", p: 1 }}>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{JSON.stringify(payload, null, 2)}</pre>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };

  // Simple visualization renderer: if visualization contains image data, show it; else show JSON
  const renderVisualization = (viz) => {
    if (!viz) return null;
    if (viz.image && typeof viz.image === "string") {
      // assume base64/data-url
      return (
        <img
          src={viz.image}
          alt="visualization"
          style={{
            width: "100%",
            maxWidth: "100%",
            maxHeight: "50vh",
            marginTop: 12,
            objectFit: "contain",
            display: "block",
          }}
        />
      );
    }
    // fallback - show JSON
    return (
      <Box sx={{ mt: 2, p: 1, background: "#f6f6f6", borderRadius: 1 }}>
        <Typography variant="subtitle2">Visualization (raw)</Typography>
        <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{JSON.stringify(viz, null, 2)}</pre>
      </Box>
    );
  };

  return (
    <StyledContainer>
      <Typography variant="h4" gutterBottom>
        DB Genie
      </Typography>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Button fullWidth variant="contained" onClick={fetchSchema} disabled={loading}>
            Refresh DB Schema
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button fullWidth variant="contained" onClick={fetchTableSample} disabled={loading}>
            Get Table Sample
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button fullWidth variant="contained" onClick={executeRawSQL} disabled={loading}>
            Execute SQL
          </Button>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Button fullWidth variant="contained" onClick={createVisualization} disabled={loading || !tableData}>
            Create Visualization
          </Button>
        </Grid>
      </Grid>

      {/* Main content: left = chat, right = data/visualization */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <Paper
            elevation={3}
            sx={{
              // Responsive heights so the chat area adapts across viewports
              height: { xs: "50vh", sm: "60vh", md: "65vh" },
              minHeight: { xs: "40vh" },
              maxHeight: "80vh",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <MessageContainer ref={messageContainerRef}>
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
                placeholder="Type your message... (you can ask for charts, SQL summaries, etc.)"
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
                    <Button onClick={handleSendStream} disabled={loading || !input.trim()} sx={{ ml: 1 }}>
                      {loading ? <CircularProgress size={24} /> : <SendIcon />}
                    </Button>
                  ),
                }}
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
            <Paper elevation={3} sx={{ height: { xs: "40vh", sm: "60vh", md: "65vh" }, maxHeight: "80vh", overflow: "auto", p: 2 }}>
            {/** Small status area for actions like refresh/sample/visualize */}
            <Box sx={{ mb: 1 }}>
              {statusMessage && (
                <Typography variant="body2" color="textSecondary">{statusMessage}</Typography>
              )}
            </Box>

            {/* Schema summary or Data preview */}
            {tableData ? (
              tableData.tables && tableData.schema ? (
                renderSchemaSummary(tableData)
              ) : (
                <Box>
                  <Typography variant="h6">Data Preview</Typography>
                  {renderTable(tableData)}
                </Box>
              )
            ) : (
              <Typography variant="body2" color="textSecondary">No data loaded. Click "Refresh DB Schema" or "Get Table Sample".</Typography>
            )}

            {/* Visualization below data preview */}
            {visualization && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Visualization</Typography>
                {renderVisualization(visualization)}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </StyledContainer>
  );
};

export default DBGenie;
