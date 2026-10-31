
import { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API = "http://127.0.0.1:8000";

const navItems = [
  { id: "overview", icon: "◫", label: "Overview" },
  { id: "dataset", icon: "▤", label: "Dataset Explorer" },
  { id: "cleaning", icon: "✧", label: "Smart Cleaning" },
  { id: "assistant", icon: "◉", label: "LLM Assistant" },
  { id: "rag", icon: "⌕", label: "RAG Knowledge" },
  { id: "mcp", icon: "⌘", label: "MCP Tools" },
];

function pretty(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

// Display the original uploaded filename instead of the backend-generated filename.
function displayFilename(dataset, originalName) {
  if (originalName) return originalName;

  if (dataset?.original_filename) {
    return dataset.original_filename;
  }

  return dataset?.filename || "—";
}

function App() {
  const [active, setActive] = useState("overview");
  const [file, setFile] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [profile, setProfile] = useState(null);
  const [cleaning, setCleaning] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "LLM Data Cleaning Assistant initialized. Upload a CSV dataset and I will assist you with profiling, anomaly detection, and smart cleaning.",
    },
  ]);

  async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.detail || data.message || "Something went wrong."
      );
    }

    return data;
  }

  async function uploadDataset(selectedFile) {
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      return setError("Please select a CSV file.");
    }

    setUploading(true);
    setError("");
    setProfile(null);
    setCleaning(null);

    try {
      const form = new FormData();
      form.append("file", selectedFile);

      const uploaded = await request("/upload", {
        method: "POST",
        body: form,
      });

      setFile(selectedFile);
      setDataset(uploaded);
      setActive("overview");

      try {
        const result = await request(
          `/profile/${encodeURIComponent(uploaded.filename)}`
        );
        setProfile(result);
      } catch {
        setProfile(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function loadCleaningPreview() {
    if (!dataset?.filename) {
      return setError("Upload a CSV dataset first.");
    }

    setBusy(true);
    setError("");

    try {
      const result = await request(
        `/clean/preview/${encodeURIComponent(dataset.filename)}`
      );

      setCleaning(result);
      setActive("cleaning");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function approveCleaning() {
    if (!dataset?.filename) return;

    setBusy(true);
    setError("");

    try {
      const result = await request(
        `/clean/approve/${encodeURIComponent(dataset.filename)}`,
        { method: "POST" }
      );

      setCleaning((previous) => ({
        ...previous,
        approvalResult: result,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function askAssistant(event) {
    event?.preventDefault();

    const text = question.trim();
    if (!text) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text },
    ]);

    setQuestion("");
    setBusy(true);
    setError("");

    try {
      const result = await request("/assistant/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: result.answer || "Empty response.",
          sources: result.rag_sources || [],
        },
      ]);
    } catch (err) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  const previewRows = Array.isArray(dataset?.preview)
    ? dataset.preview
    : [];

  const columns =
    previewRows.length > 0 ? Object.keys(previewRows[0]) : [];

  const profileEntries =
    profile && typeof profile === "object"
      ? Object.entries(profile).filter(
          ([key]) =>
            !["preview", "sample", "data"].includes(key.toLowerCase())
        )
      : [];

  function renderOverview() {
    return (
      <>
        <div className="welcome-row">
          <div>
            <div className="eyebrow">
              LLM WORKSPACE // SYSTEM READY
            </div>

            <h1>
              Make your data <span>intelligent.</span>
            </h1>

            <p className="welcome-copy">
              Explore, understand and clean datasets using generative AI,
              semantic retrieval, and structured agentic workflows.
            </p>
          </div>
        </div>

        <div className="pipeline-container">
          <svg
            className="neural-svg"
            viewBox="0 0 1000 300"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient
                id="lineGradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="0%"
              >
                <stop offset="0%" stopColor="var(--neon-blue)" />
                <stop offset="50%" stopColor="var(--neon-cyan)" />
                <stop offset="100%" stopColor="var(--neon-purple)" />
              </linearGradient>
            </defs>

            <path
              className="path-bg"
              d="M 100 150 C 200 150, 200 80, 300 80"
            />
            <path
              className="path-glow"
              d="M 100 150 C 200 150, 200 80, 300 80"
            />

            <path
              className="path-bg"
              d="M 300 80 C 400 80, 400 150, 500 150"
            />
            <path
              className="path-glow"
              d="M 300 80 C 400 80, 400 150, 500 150"
            />

            <path
              className="path-bg"
              d="M 500 150 C 600 150, 600 220, 700 220"
            />
            <path
              className="path-glow"
              d="M 500 150 C 600 150, 600 220, 700 220"
            />

            <path
              className="path-bg"
              d="M 700 220 C 800 220, 800 150, 900 150"
            />
            <path
              className="path-glow"
              d="M 700 220 C 800 220, 800 150, 900 150"
            />
          </svg>

          <div className="node" style={{ left: "10%", top: "50%" }}>
            <div className="node-icon">⇧</div>
            <div className="node-text">CSV Dataset</div>
            <div className="node-sub">Ingestion</div>
          </div>

          <div
            className="node purple"
            style={{ left: "30%", top: "26.6%" }}
          >
            <div className="node-icon">⌘</div>
            <div className="node-text">MCP Tools</div>
            <div className="node-sub">Profiling</div>
          </div>

          <div className="node" style={{ left: "50%", top: "50%" }}>
            <div className="node-icon">⌕</div>
            <div className="node-text">RAG Engine</div>
            <div className="node-sub">Context</div>
          </div>

          <div
            className="node green"
            style={{ left: "70%", top: "73.3%" }}
          >
            <div className="node-icon">✳</div>
            <div className="node-text">LLM Reasoning</div>
            <div className="node-sub">Generation</div>
          </div>

          <div className="node green" style={{ left: "90%", top: "50%" }}>
            <div className="node-icon">✓</div>
            <div className="node-text">Clean Dataset</div>
            <div className="node-sub">Export</div>
          </div>
        </div>

        <section className="engine-grid">
          <article className="engine-card">
            <div className="engine-symbol purple">⌘</div>
            <h3>MCP Tool Server</h3>
            <p>
              Structured tools for dataset inspection, missing values,
              duplicates and column summaries.
            </p>

            <button
              className="primary-button"
              onClick={() => setActive("mcp")}
            >
              Explore Tools →
            </button>
          </article>

          <article className="engine-card">
            <div className="engine-symbol blue">⌕</div>
            <h3>RAG Knowledge Engine</h3>
            <p>
              Retrieves relevant data-cleaning guidance to provide
              context-grounded responses.
            </p>

            <button
              className="primary-button"
              onClick={() => setActive("rag")}
            >
              Explore RAG →
            </button>
          </article>

          <article className="engine-card">
            <div className="engine-symbol teal">✳</div>
            <h3>LLM Assistant</h3>
            <p>
              Ask natural-language questions and receive explanations
              and data-cleaning guidance.
            </p>

            <button
              className="primary-button"
              onClick={() => setActive("assistant")}
            >
              Open Assistant →
            </button>
          </article>
        </section>

        <section className="workspace-grid">
          <div className="panel" style={{ padding: "40px" }}>
            <div className="eyebrow">01 // DATA INGESTION</div>

            <h2 style={{ color: "#fff", marginBottom: "20px" }}>
              Bring your dataset
            </h2>

            {/* Fixed dropzone alignment */}
            <label
              className="dropzone"
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                minHeight: "180px",
              }}
            >
              <input
                type="file"
                accept=".csv"
                style={{ display: "none" }}
                onChange={(event) =>
                  uploadDataset(event.target.files?.[0])
                }
              />

              <span className="drop-icon">↑</span>

              <strong
                style={{
                  color: "#fff",
                  display: "block",
                  marginBottom: "10px",
                  fontSize: "16px",
                }}
              >
                {uploading ? "Uploading..." : "Choose a CSV file"}
              </strong>

              <span
                style={{
                  fontFamily: "var(--font-code)",
                  fontSize: "12px",
                  color: "#8892b0",
                }}
              >
                CLICK TO BROWSE // MAX 10MB
              </span>
            </label>

            {dataset && (
              <div
                style={{
                  marginTop: "20px",
                  padding: "15px",
                  background: "rgba(0,255,136,0.1)",
                  border: "1px solid rgba(0,255,136,0.3)",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  gap: "15px",
                }}
              >
                <span
                  style={{
                    background: "var(--neon-green)",
                    color: "#000",
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontWeight: "bold",
                  }}
                >
                  CSV
                </span>

                <div>
                  <strong style={{ color: "#fff", display: "block" }}>
                    {displayFilename(dataset, file?.name)}
                  </strong>

                  <small style={{ color: "#8892b0" }}>
                    {dataset.rows} rows · {dataset.columns} cols
                  </small>
                </div>
              </div>
            )}
          </div>

          <div className="panel" style={{ padding: "40px" }}>
            <div className="eyebrow">02 // ACTIVE WORKSPACE</div>

            <h2 style={{ color: "#fff", marginBottom: "20px" }}>
              Dataset snapshot
            </h2>

            {dataset ? (
              <div>
                <div
                  style={{
                    fontFamily: "var(--font-code)",
                    color: "var(--neon-cyan)",
                    marginBottom: "20px",
                    wordBreak: "break-all",
                  }}
                >
                  {displayFilename(dataset, file?.name)}
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "30px",
                    marginBottom: "30px",
                  }}
                >
                  <div>
                    <strong
                      style={{
                        fontFamily: "var(--font-code)",
                        fontSize: "32px",
                        color: "#fff",
                        display: "block",
                      }}
                    >
                      {dataset.rows ?? "—"}
                    </strong>

                    <small style={{ color: "#8892b0", letterSpacing: "1px" }}>
                      ROWS
                    </small>
                  </div>

                  <div>
                    <strong
                      style={{
                        fontFamily: "var(--font-code)",
                        fontSize: "32px",
                        color: "#fff",
                        display: "block",
                      }}
                    >
                      {dataset.columns ?? "—"}
                    </strong>

                    <small style={{ color: "#8892b0", letterSpacing: "1px" }}>
                      COLUMNS
                    </small>
                  </div>
                </div>

                <button
                  className="primary-button"
                  onClick={() => setActive("dataset")}
                >
                  Explore Dataset →
                </button>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "40px 0" }}>
                <span
                  style={{
                    fontSize: "40px",
                    color: "rgba(255,255,255,0.1)",
                  }}
                >
                  ▤
                </span>

                <p
                  style={{
                    marginTop: "15px",
                    fontFamily: "var(--font-code)",
                    fontSize: "12px",
                  }}
                >
                  AWAITING DATA STREAM...
                </p>
              </div>
            )}
          </div>
        </section>
      </>
    );
  }

  function renderDataset() {
    return (
      <section>
        <div className="eyebrow">DATA WORKSPACE / EXPLORER</div>
        <h1>Dataset Explorer</h1>

        {!dataset ? (
          <div
            className="panel"
            style={{
              padding: "80px",
              textAlign: "center",
              marginTop: "30px",
            }}
          >
            <span
              style={{
                fontSize: "50px",
                color: "var(--neon-cyan)",
                filter: "drop-shadow(0 0 20px var(--neon-cyan))",
              }}
            >
              ▤
            </span>

            <h2 style={{ color: "#fff", margin: "20px 0" }}>
              NO DATASET DETECTED
            </h2>

            <button
              className="primary-button"
              onClick={() => setActive("overview")}
            >
              Go to Overview
            </button>
          </div>
        ) : (
          <>
            <div className="engine-grid" style={{ marginTop: "30px" }}>
              <div className="panel" style={{ padding: "30px" }}>
                <div className="eyebrow">FILE</div>

                <strong
                  style={{
                    color: "var(--neon-cyan)",
                    fontSize: "18px",
                    display: "block",
                    marginTop: "10px",
                    wordBreak: "break-all",
                  }}
                >
                  {displayFilename(dataset, file?.name)}
                </strong>
              </div>

              <div className="panel" style={{ padding: "30px" }}>
                <div className="eyebrow">TOTAL ROWS</div>

                <strong
                  style={{
                    fontFamily: "var(--font-code)",
                    fontSize: "32px",
                    color: "#fff",
                    display: "block",
                    marginTop: "5px",
                  }}
                >
                  {dataset.rows ?? "—"}
                </strong>
              </div>

              <div className="panel" style={{ padding: "30px" }}>
                <div className="eyebrow">TOTAL COLUMNS</div>

                <strong
                  style={{
                    fontFamily: "var(--font-code)",
                    fontSize: "32px",
                    color: "#fff",
                    display: "block",
                    marginTop: "5px",
                  }}
                >
                  {dataset.columns ?? "—"}
                </strong>
              </div>
            </div>

            <div
              className="panel"
              style={{ padding: "30px", marginTop: "30px" }}
            >
              <div className="eyebrow">SAMPLE RECORDS</div>

              <h2 style={{ color: "#fff", margin: "10px 0 20px" }}>
                Data Preview
              </h2>

              {previewRows.length ? (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        {columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {previewRows.map((row, i) => (
                        <tr key={i}>
                          {columns.map((col) => (
                            <td key={col}>{pretty(row[col])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No preview data.</p>
              )}
            </div>
          </>
        )}
      </section>
    );
  }

  function renderCleaning() {
    return (
      <section>
        <div className="eyebrow">DATA QUALITY / TRANSFORMATION</div>
        <h1>Smart Cleaning</h1>

        <div
          className="panel"
          style={{ padding: "40px", marginTop: "30px", maxWidth: "1000px" }}
        >
          <div className="eyebrow">03 // CLEANING WORKFLOW</div>

          <h2 style={{ color: "#fff", margin: "10px 0 20px" }}>
            Transformations
          </h2>

          {!dataset ? (
            <p>Upload a dataset first.</p>
          ) : (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "15px",
                  marginBottom: "30px",
                }}
              >
                <span
                  style={{
                    background: "var(--neon-green)",
                    color: "#000",
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    fontWeight: "bold",
                  }}
                >
                  CSV
                </span>

                <div>
                  <strong style={{ color: "#fff" }}>
                    {displayFilename(dataset, file?.name)}
                  </strong>
                </div>
              </div>

              <button
                className="primary-button"
                disabled={busy}
                onClick={loadCleaningPreview}
              >
                {busy ? "GENERATING..." : "GENERATE CLEANING PREVIEW →"}
              </button>
            </>
          )}

          {cleaning && (
            <div style={{ marginTop: "40px" }}>
              <div className="eyebrow" style={{ marginBottom: "15px" }}>
                PROPOSED ACTIONS
              </div>

              <pre className="json-output">
                {JSON.stringify(cleaning.actions ?? cleaning, null, 2)}
              </pre>

              {cleaning.approvalResult ? (
                <div
                  style={{
                    padding: "20px",
                    background: "rgba(0,255,136,0.1)",
                    border: "1px solid rgba(0,255,136,0.3)",
                    color: "var(--neon-green)",
                    borderRadius: "12px",
                    marginTop: "20px",
                    fontFamily: "var(--font-code)",
                  }}
                >
                  ✓ CLEANING SUCCESSFUL. Result:{" "}
                  {pretty(cleaning.approvalResult)}
                </div>
              ) : (
                <button
                  className="primary-button"
                  style={{ marginTop: "20px" }}
                  disabled={busy}
                  onClick={approveCleaning}
                >
                  {busy ? "APPLYING..." : "APPROVE & APPLY"}
                </button>
              )}
            </div>
          )}
        </div>
      </section>
    );
  }

  function renderAssistant() {
    return (
      <section>
        <div className="eyebrow">GENERATIVE AI / NATURAL LANGUAGE</div>
        <h1>LLM Assistant</h1>

        <div
          className="chat-panel"
          style={{ marginTop: "30px", maxWidth: "1000px" }}
        >
          <div className="chat-header">
            <div className="chat-avatar">✳</div>

            <div>
              <strong style={{ color: "#fff", fontSize: "16px" }}>
                LLM Data Assistant
              </strong>

              <small
                style={{
                  color: "var(--neon-green)",
                  display: "block",
                  marginTop: "5px",
                  fontFamily: "var(--font-code)",
                }}
              >
                ● RAG PIPELINE ONLINE
              </small>
            </div>

            <span
              style={{
                marginLeft: "auto",
                fontFamily: "var(--font-code)",
                background: "rgba(176,38,255,0.15)",
                color: "#d8b4fe",
                padding: "8px 16px",
                borderRadius: "20px",
                border: "1px solid rgba(176,38,255,0.3)",
              }}
            >
              RAG + LLM
            </span>
          </div>

          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  gap: "15px",
                  justifyContent:
                    msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                {msg.role === "assistant" && (
                  <div
                    style={{
                      width: "35px",
                      height: "35px",
                      borderRadius: "10px",
                      background: "rgba(0,240,255,0.1)",
                      border: "1px solid var(--neon-cyan)",
                      color: "var(--neon-cyan)",
                      display: "grid",
                      placeItems: "center",
                    }}
                  >
                    ✳
                  </div>
                )}

                <div className={`message-bubble ${msg.role}`}>
                  <div style={{ color: "#e2e8f0" }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.text}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <form className="chat-input-area" onSubmit={askAssistant}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Query the RAG engine..."
            />

            <button
              className="send-button"
              disabled={busy || !question.trim()}
            >
              ↑
            </button>
          </form>
        </div>
      </section>
    );
  }

  function renderRag() {
    return (
      <section>
        <div className="eyebrow">RETRIEVAL AUGMENTED GENERATION</div>
        <h1>RAG Architecture</h1>

        <div
          className="panel"
          style={{
            padding: "50px",
            marginTop: "30px",
            background:
              "radial-gradient(circle at top right, rgba(176,38,255,0.1), transparent 50%)",
          }}
        >
          <h2 style={{ color: "#fff", fontSize: "28px", marginBottom: "20px" }}>
            Retrieve before generating
          </h2>

          <p style={{ maxWidth: "800px", fontSize: "16px" }}>
            The system uses ChromaDB and advanced text embeddings to retrieve
            relevant knowledge chunks before injecting them into the LLM
            context window.
          </p>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "20px",
              marginTop: "50px",
              flexWrap: "wrap",
              fontFamily: "var(--font-code)",
            }}
          >
            <div
              style={{
                padding: "20px 30px",
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "12px",
                color: "#fff",
              }}
            >
              Knowledge Base
            </div>

            <div style={{ color: "var(--neon-cyan)", fontSize: "24px" }}>
              →
            </div>

            <div
              style={{
                padding: "20px 30px",
                background: "rgba(0,240,255,0.05)",
                border: "1px solid rgba(0,240,255,0.2)",
                borderRadius: "12px",
                color: "var(--neon-cyan)",
              }}
            >
              Embeddings
            </div>

            <div style={{ color: "var(--neon-cyan)", fontSize: "24px" }}>
              →
            </div>

            <div
              style={{
                padding: "20px 30px",
                background: "rgba(176,38,255,0.1)",
                border: "1px solid rgba(176,38,255,0.3)",
                borderRadius: "12px",
                color: "#d8b4fe",
                boxShadow: "0 0 20px rgba(176,38,255,0.2)",
              }}
            >
              ChromaDB
            </div>

            <div style={{ color: "var(--neon-cyan)", fontSize: "24px" }}>
              →
            </div>

            <div
              style={{
                padding: "20px 30px",
                background: "rgba(0,255,136,0.1)",
                border: "1px solid rgba(0,255,136,0.3)",
                borderRadius: "12px",
                color: "var(--neon-green)",
                boxShadow: "0 0 20px rgba(0,255,136,0.2)",
              }}
            >
              LLM Context
            </div>
          </div>
        </div>
      </section>
    );
  }

  function renderMcp() {
    const tools = [
      [
        "inspect_dataset",
        "Inspect Dataset",
        "Explore dataset structure.",
      ],
      [
        "detect_missing_values",
        "Detect Missing Values",
        "Identify null counts.",
      ],
      [
        "detect_duplicates",
        "Detect Duplicates",
        "Find duplicate records.",
      ],
      [
        "summarize_column",
        "Summarize Column",
        "Generate a statistical summary of a selected column.",
      ],
      [
        "detect_outliers",
        "Detect Outliers",
        "Identify unusual numerical values using the IQR method.",
      ],
    ];

    return (
      <section>
        <div className="eyebrow">MODEL CONTEXT PROTOCOL</div>
        <h1>MCP Tool Centre</h1>

        <div style={{ marginTop: "30px" }}>
          {tools.map(([name, title, desc], i) => (
            <div className="tool-card" key={name}>
              <div className="tool-index">0{i + 1}</div>

              <div>
                <strong
                  style={{
                    color: "#fff",
                    fontSize: "16px",
                    display: "block",
                  }}
                >
                  {title}
                </strong>

                <code>{name}</code>

                <p style={{ margin: "10px 0 0", fontSize: "13px" }}>
                  {desc}
                </p>
              </div>

              <div className="tool-type">ACTIVE MODULE</div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  const pageTitles = {
    overview: "Overview",
    dataset: "Dataset Explorer",
    cleaning: "Smart Cleaning",
    assistant: "LLM Assistant",
    rag: "RAG Knowledge",
    mcp: "MCP Tools",
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span>✳</span>
          </div>

          <div className="brand-name">
            LLM ASSISTANT
            <span>DATA CLEANING</span>
          </div>
        </div>

        <nav className="side-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                active === item.id ? "active" : ""
              }`}
              onClick={() => setActive(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            LLM Studio <span>/</span> {pageTitles[active]}
          </div>

          <div className="user-avatar">AI</div>
        </header>

        <div className="page-content">
          {error && (
            <div
              style={{
                background: "rgba(255,51,102,0.1)",
                border: "1px solid #ff3366",
                color: "#ff3366",
                padding: "15px",
                borderRadius: "8px",
                marginBottom: "30px",
                fontFamily: "var(--font-code)",
              }}
            >
              ERROR: {error}
            </div>
          )}

          {active === "overview" && renderOverview()}
          {active === "dataset" && renderDataset()}
          {active === "cleaning" && renderCleaning()}
          {active === "assistant" && renderAssistant()}
          {active === "rag" && renderRag()}
          {active === "mcp" && renderMcp()}
        </div>
      </main>
    </div>
  );
}

export default App;
