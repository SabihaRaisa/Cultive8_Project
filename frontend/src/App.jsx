
import { useRef, useState } from "react";
import {
  Shield,
  Upload,
  FileText,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Search,
  Clock,
  Server,
  ChevronDown,
  ChevronUp,
  LoaderCircle,
  ShieldAlert,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function severityClass(severity) {
  return (severity || "Low").toLowerCase();
}

function App() {
  const fileInput = useRef(null);

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);
  const [runId, setRunId] = useState("");
  const [lookupId, setLookupId] = useState("");
  const [expandedFinding, setExpandedFinding] = useState(null);

  const handleFileChange = (selectedFile) => {
    setError("");
    setReport(null);

    if (!selectedFile) return;

    const extension = selectedFile.name.split(".").pop().toLowerCase();

    if (!["log", "txt"].includes(extension)) {
      setError("Only .log and .txt files are supported.");
      setFile(null);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size cannot exceed 10 MB.");
      setFile(null);
      return;
    }

    if (selectedFile.size === 0) {
      setError("The selected file is empty.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const uploadAndAnalyze = async () => {
    if (!file) {
      setError("Please select a log file first.");
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);
    setRunId("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/logs/upload`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Analysis request failed."
        );
      }

      const data = result.data;
      const id = data.run_id;

      if (!id) {
        throw new Error("The backend did not return an analysis Run ID.");
      }

      setRunId(String(id));

      // Prefer the report returned by the upload endpoint.
      if (data.report) {
        setReport(data.report);
      } else {
        await fetchReport(id);
      }
    } catch (err) {
      setError(err.message || "Unable to connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  const fetchReport = async (id) => {
    const response = await fetch(`${API_URL}/api/reports/${id}`);
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Could not retrieve the report.");
    }

    setReport(result.data);
    setRunId(String(id));
    setError("");
  };

  const handleLookup = async (event) => {
    event.preventDefault();

    if (!lookupId.trim() || !/^\d+$/.test(lookupId.trim())) {
      setError("Enter a valid numeric Run ID.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await fetchReport(lookupId.trim());
    } catch (err) {
      setReport(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const summary = report?.summary || {};
  const findings = report?.findings || [];
  const chunks = report?.chunks || [];
  const run = report?.run || {};

  const severityCounts = summary.severity_counts || {};

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Shield size={23} />
          </div>
          <div>
            <h1>LogGuard AI</h1>
            <p>Local Security Log Analyzer</p>
          </div>
        </div>

        <div className="connection">
          <span className="online-dot"></span>
          Local AI Analysis
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <div className="eyebrow">
            <ShieldAlert size={15} />
            AI-POWERED SECURITY MONITORING
          </div>

          <h2>
            Understand your server logs.
            <br />
            <span>Detect suspicious activity.</span>
          </h2>

          <p>
            Upload your server logs and analyze suspicious events using
            a locally running AI model.
          </p>
        </section>

        <section className="upload-card">
          <div className="section-heading">
            <div className="heading-icon">
              <Upload size={20} />
            </div>
            <div>
              <h3>Upload Security Log</h3>
              <p>Select a server log file to begin analysis.</p>
            </div>
          </div>

          <div
            className={`dropzone ${file ? "has-file" : ""}`}
            onClick={() => !loading && fileInput.current?.click()}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              if (!loading) {
                handleFileChange(event.dataTransfer.files[0]);
              }
            }}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (
                (event.key === "Enter" || event.key === " ") &&
                !loading
              ) {
                fileInput.current?.click();
              }
            }}
          >
            <input
              ref={fileInput}
              type="file"
              accept=".log,.txt"
              hidden
              onChange={(event) =>
                handleFileChange(event.target.files[0])
              }
            />

            <div className="upload-icon">
              {file ? <FileText size={28} /> : <Upload size={28} />}
            </div>

            {file ? (
              <>
                <h4>{file.name}</h4>
                <p>{(file.size / 1024).toFixed(2)} KB · Ready to analyze</p>
              </>
            ) : (
              <>
                <h4>Drop your log file here</h4>
                <p>or click to browse your computer</p>
              </>
            )}

            <span className="file-requirements">
              Supported formats: .log, .txt · Maximum size: 10 MB
            </span>
          </div>

          {file && !loading && (
            <button
              className="remove-file"
              onClick={() => {
                setFile(null);
                if (fileInput.current) fileInput.current.value = "";
              }}
            >
              Remove selected file
            </button>
          )}

          <button
            className="analyze-button"
            onClick={uploadAndAnalyze}
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <LoaderCircle className="spin" size={19} />
                Analyzing with Local AI...
              </>
            ) : (
              <>
                <Activity size={19} />
                Start Security Analysis
              </>
            )}
          </button>

          {loading && (
            <div className="loading-panel">
              <div className="loading-title">
                <LoaderCircle className="spin" size={19} />
                AI analysis is running
              </div>
              <div className="progress-track">
                <div className="progress-bar"></div>
              </div>
              <p>
                Your log is being processed locally. Large files may take
                longer. Please keep this page open.
              </p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <XCircle size={19} />
              {error}
            </div>
          )}
        </section>

        <section className="lookup-card">
          <div>
            <h3>Retrieve Previous Report</h3>
            <p>Enter an existing analysis Run ID.</p>
          </div>

          <form onSubmit={handleLookup}>
            <input
              type="number"
              min="1"
              placeholder="Example: 1"
              value={lookupId}
              onChange={(event) => setLookupId(event.target.value)}
            />
            <button type="submit" disabled={loading}>
              <Search size={17} />
              Find Report
            </button>
          </form>
        </section>

        {report && (
          <section className="report-section">
            <div className="report-heading">
              <div>
                <div className="eyebrow">
                  <CheckCircle size={15} />
                  ANALYSIS REPORT
                </div>
                <h2>Security Analysis Results</h2>
                <p>
                  File: {run.file_name || "Uploaded log"} · Run ID: {runId}
                </p>
              </div>

              <button
                className="refresh-button"
                onClick={() => fetchReport(runId)}
                disabled={loading}
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>

            <div className="status-banner">
              <div className="status-icon">
                {run.status === "completed" ? (
                  <CheckCircle size={22} />
                ) : (
                  <AlertTriangle size={22} />
                )}
              </div>
              <div>
                <strong>
                  Analysis {run.status || "available"}
                </strong>
                <p>
                  {run.created_at
                    ? `Created: ${new Date(run.created_at).toLocaleString()}`
                    : "Report retrieved successfully."}
                </p>
              </div>
              <span className={`status-tag ${run.status || "unknown"}`}>
                {run.status || "Unknown"}
              </span>
            </div>

            <div className="stats-grid">
              <StatCard
                label="Total Findings"
                value={summary.total_findings ?? 0}
                icon={<ShieldAlert size={20} />}
              />
              <StatCard
                label="High Severity"
                value={severityCounts.High ?? 0}
                icon={<AlertTriangle size={20} />}
              />
              <StatCard
                label="Critical"
                value={severityCounts.Critical ?? 0}
                icon={<XCircle size={20} />}
              />
              <StatCard
                label="Chunks Analyzed"
                value={`${summary.completed_chunks ?? 0}/${summary.total_chunks ?? 0}`}
                icon={<FileText size={20} />}
              />
            </div>

            <div className="severity-card">
              <h3>Severity Distribution</h3>
              <div className="severity-grid">
                {["Critical", "High", "Medium", "Low"].map((level) => (
                  <div className="severity-item" key={level}>
                    <span className={`severity-dot ${severityClass(level)}`} />
                    <span>{level}</span>
                    <strong>{severityCounts[level] ?? 0}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="findings-card">
              <div className="findings-heading">
                <div>
                  <h3>Detected Findings</h3>
                  <p>Consolidated security observations from your logs.</p>
                </div>
                <span className="finding-count">
                  {findings.length} findings
                </span>
              </div>

              {findings.length === 0 ? (
                <div className="empty-findings">
                  <CheckCircle size={30} />
                  <h4>No suspicious findings returned</h4>
                  <p>
                    This analysis did not return validated security findings.
                    It does not guarantee that the logs are threat-free.
                  </p>
                </div>
              ) : (
                <div className="finding-list">
                  {findings.map((finding, index) => {
                    const expanded = expandedFinding === index;

                    return (
                      <article className="finding" key={index}>
                        <button
                          className="finding-top"
                          onClick={() =>
                            setExpandedFinding(expanded ? null : index)
                          }
                        >
                          <div className="finding-main">
                            <span
                              className={`severity-badge ${severityClass(finding.severity)}`}
                            >
                              {finding.severity}
                            </span>
                            <div>
                              <h4>{finding.attack_type}</h4>
                              <p>
                                Identifier: {finding.identifier || "Unknown"}
                              </p>
                            </div>
                          </div>
                          {expanded ? (
                            <ChevronUp size={20} />
                          ) : (
                            <ChevronDown size={20} />
                          )}
                        </button>

                        {expanded && (
                          <div className="finding-details">
                            <Detail label="Evidence" value={finding.evidence} />
                            <Detail label="Reason" value={finding.reason} />
                            <Detail
                              label="Suggested Action"
                              value={finding.suggested_action}
                            />
                            <div className="detail-row">
                              <strong>Original line numbers</strong>
                              <span>
                                {Array.isArray(finding.line_numbers)
                                  ? finding.line_numbers.join(", ")
                                  : "Not available"}
                              </span>
                            </div>
                            {finding.source_chunks && (
                              <div className="detail-row">
                                <strong>Source chunks</strong>
                                <span>{finding.source_chunks.join(", ")}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </article>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="technical-card">
              <h3>Processing Details</h3>
              <div className="technical-grid">
                <Detail
                  label="Processing time"
                  value={`${summary.processing_time_seconds ?? 0} seconds`}
                />
                <Detail
                  label="Prompt tokens"
                  value={summary.prompt_tokens ?? 0}
                />
                <Detail
                  label="Output tokens"
                  value={summary.output_tokens ?? 0}
                />
                <Detail
                  label="Failed chunks"
                  value={summary.failed_chunks ?? 0}
                />
                <Detail
                  label="Raw findings"
                  value={summary.raw_findings ?? 0}
                />
                <Detail
                  label="Database Run ID"
                  value={run.id ?? runId}
                />
              </div>
            </div>

            {chunks.length > 0 && (
              <div className="chunks-card">
                <h3>Chunk Processing Status</h3>
                {chunks.map((chunk) => (
                  <div className="chunk-row" key={chunk.id}>
                    <span>Chunk {chunk.chunk_number}</span>
                    <span>{chunk.status}</span>
                    <span>
                      {chunk.processing_time ?? 0}s
                    </span>
                    {chunk.error && (
                      <span className="chunk-error">{chunk.error}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        <footer>
          <div className="footer-brand">
            <Shield size={17} />
            LogGuard AI
          </div>
          <p>
            Local AI Security Log Analyzer · Powered by FastAPI and Ollama
          </p>
          <p className="privacy-note">
            Log analysis is performed using your local backend and local model.
          </p>
        </footer>
      </main>
    </div>
  );
}

function StatCard({ label, value, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div className="detail-block">
      <strong>{label}</strong>
      <p>{value || "Not available"}</p>
    </div>
  );
}

export default App;
