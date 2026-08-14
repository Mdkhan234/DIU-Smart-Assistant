import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function AdminDashboard() {
  const [stats, setStats] = useState({
    total_documents: 0,
    total_pages: 0,
    total_chunks: 0,
  });

  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadStats = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/admin/documents");

      setStats({
        total_documents: response.data.total_documents || 0,
        total_pages: response.data.total_pages || 0,
        total_chunks: response.data.total_chunks || 0,
      });
    } catch (err) {
      console.error("Dashboard error:", err);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const rebuildDatabase = async () => {
    const confirmed = window.confirm(
      "Rebuild the knowledge base?\n\nAll uploaded PDFs will be processed again and the vector database will be recreated."
    );

    if (!confirmed || rebuilding) return;

    try {
      setRebuilding(true);
      setMessage("");
      setError("");

      const response = await api.post(
        "/admin/rebuild-vector-db"
      );

      if (response.data.success) {
        const details = response.data.details || {};

        setMessage(
          `Knowledge base rebuilt successfully. ${details.chunks || 0} chunks indexed.`
        );

        await loadStats();
      } else {
        setError(
          response.data.message ||
            "Knowledge base rebuild failed."
        );
      }
    } catch (err) {
      console.error("Rebuild error:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to rebuild vector database."
      );
    } finally {
      setRebuilding(false);
    }
  };

  const statCards = [
    {
      label: "Documents",
      value: stats.total_documents,
      icon: "DOC",
      description: "Uploaded PDF files",
    },
    {
      label: "Pages",
      value: stats.total_pages,
      icon: "PDF",
      description: "Total indexed pages",
    },
    {
      label: "Chunks",
      value: stats.total_chunks,
      icon: "DB",
      description: "Searchable knowledge chunks",
    },
  ];

  return (
    <div className="admin-page">

      {/* HEADER */}
      <header className="admin-header">

        <div className="admin-brand">

          <div className="admin-logo">
            DIU
          </div>

          <div>
            <h1>DIU Smart Assistant</h1>
            <p>Administrator Portal</p>
          </div>

        </div>

        <Link
          to="/"
          className="admin-back-button"
        >
          ← Back to Chat
        </Link>

      </header>


      {/* MAIN */}
      <main className="admin-main">

        {/* HERO */}
        <section className="admin-hero">

          <div>
            <span className="admin-eyebrow">
              ADMINISTRATION
            </span>

            <h2>Knowledge Base Dashboard</h2>

            <p>
              Manage DIU documents and maintain the
              university knowledge base used by the
              AI assistant.
            </p>
          </div>

          <div className="admin-status">

            <span className="status-dot"></span>

            <div>
              <strong>Knowledge Base</strong>
              <span>
                {loading
                  ? "Checking..."
                  : "System available"}
              </span>
            </div>

          </div>

        </section>


        {/* MESSAGE */}
        {message && (
          <div className="admin-alert admin-alert-success">
            <span>✓</span>
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="admin-alert admin-alert-error">
            <span>!</span>
            <span>{error}</span>
          </div>
        )}


        {/* STATISTICS */}
        <section className="admin-stats">

          {statCards.map((card) => (
            <div
              className="admin-stat-card"
              key={card.label}
            >

              <div className="admin-stat-top">

                <div className="admin-stat-icon">
                  {card.icon}
                </div>

              </div>

              <div className="admin-stat-value">

                {loading
                  ? "—"
                  : card.value.toLocaleString()}

              </div>

              <div className="admin-stat-label">
                {card.label}
              </div>

              <div className="admin-stat-description">
                {card.description}
              </div>

            </div>
          ))}

        </section>


        {/* QUICK ACTIONS */}
        <section className="admin-section">

          <div className="admin-section-header">

            <div>
              <h3>Quick Actions</h3>

              <p>
                Manage documents and update the
                knowledge base.
              </p>
            </div>

          </div>


          <div className="admin-actions">

            <Link
              to="/admin/documents"
              className="admin-action-card"
            >

              <div className="admin-action-icon">
                DOC
              </div>

              <div className="admin-action-content">
                <strong>Manage Documents</strong>

                <span>
                  Upload, view and delete PDF documents.
                </span>
              </div>

              <span className="admin-action-arrow">
                →
              </span>

            </Link>


            <button
              className="admin-action-card admin-action-button"
              onClick={rebuildDatabase}
              disabled={rebuilding}
            >

              <div className="admin-action-icon">
                DB
              </div>

              <div className="admin-action-content">
                <strong>
                  {rebuilding
                    ? "Rebuilding..."
                    : "Rebuild Knowledge Base"}
                </strong>

                <span>
                  Re-process all uploaded PDFs and
                  recreate the vector database.
                </span>
              </div>

              <span className="admin-action-arrow">
                {rebuilding ? "..." : "→"}
              </span>

            </button>


            <Link
              to="/"
              className="admin-action-card"
            >

              <div className="admin-action-icon">
                AI
              </div>

              <div className="admin-action-content">
                <strong>Open AI Assistant</strong>

                <span>
                  Test the RAG chatbot with the current
                  knowledge base.
                </span>
              </div>

              <span className="admin-action-arrow">
                →
              </span>

            </Link>

          </div>

        </section>


        {/* SYSTEM INFORMATION */}
        <section className="admin-section">

          <div className="admin-section-header">

            <div>
              <h3>System Information</h3>

              <p>
                Current DIU Smart Assistant configuration.
              </p>
            </div>

          </div>


          <div className="admin-info-grid">

            <div className="admin-info-item">
              <span>AI Pipeline</span>
              <strong>RAG</strong>
            </div>

            <div className="admin-info-item">
              <span>Vector Database</span>
              <strong>ChromaDB</strong>
            </div>

            <div className="admin-info-item">
              <span>Embeddings</span>
              <strong>all-MiniLM-L6-v2</strong>
            </div>

            <div className="admin-info-item">
              <span>LLM</span>
              <strong>Gemini</strong>
            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

export default AdminDashboard;