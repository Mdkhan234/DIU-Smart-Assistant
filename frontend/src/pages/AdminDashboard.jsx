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

  const loadStats = async () => {
    try {
      setLoading(true);

      const response = await api.get("/admin/documents");

      setStats({
        total_documents: response.data.total_documents || 0,
        total_pages: response.data.total_pages || 0,
        total_chunks: response.data.total_chunks || 0,
      });

    } catch (error) {
      console.error(error);
      setMessage("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const rebuildDatabase = async () => {
    try {
      setRebuilding(true);
      setMessage("");

      const response = await api.post(
        "/admin/rebuild-vector-db"
      );

      if (response.data.success) {
        setMessage(
          `Knowledge base rebuilt successfully. ${response.data.details.chunks} chunks indexed.`
        );

        await loadStats();
      }

    } catch (error) {
      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Failed to rebuild vector database."
      );
    } finally {
      setRebuilding(false);
    }
  };

  return (
    <div className="admin-page">

      {/* Header */}
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
          ← User Chat
        </Link>

      </header>


      {/* Main */}
      <main className="admin-content">

        <div className="admin-title-section">

          <div>
            <span className="admin-eyebrow">
              ADMINISTRATION
            </span>

            <h2>Dashboard</h2>

            <p>
              Manage the DIU Smart Assistant knowledge base.
            </p>
          </div>

          <button
            className="rebuild-button"
            onClick={rebuildDatabase}
            disabled={rebuilding}
          >
            {rebuilding
              ? "Rebuilding..."
              : "↻ Rebuild Knowledge Base"}
          </button>

        </div>


        {/* Stats */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-icon">
              📄
            </div>

            <div>
              <span>Total Documents</span>
              <strong>
                {loading ? "—" : stats.total_documents}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              📑
            </div>

            <div>
              <span>Total Pages</span>
              <strong>
                {loading ? "—" : stats.total_pages}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              🧩
            </div>

            <div>
              <span>Total Chunks</span>
              <strong>
                {loading ? "—" : stats.total_chunks}
              </strong>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon success">
              ✓
            </div>

            <div>
              <span>Knowledge Base</span>
              <strong className="indexed">
                Ready
              </strong>
            </div>

          </div>

        </section>


        {/* Message */}

        {message && (
          <div className="admin-notification">
            {message}
          </div>
        )}


        {/* Management */}

        <section className="admin-actions">

          <Link
            to="/admin/documents"
            className="admin-action-card"
          >

            <div className="action-icon">
              📚
            </div>

            <div>
              <h3>Documents</h3>
              <p>
                Upload, view and delete university documents.
              </p>
            </div>

            <span className="action-arrow">
              →
            </span>

          </Link>


          <div className="admin-action-card">

            <div className="action-icon">
              🧠
            </div>

            <div>
              <h3>Knowledge Base</h3>
              <p>
                Rebuild the vector database after document changes.
              </p>
            </div>

            <span className="action-status">
              Active
            </span>

          </div>

        </section>

      </main>

    </div>
  );
}

export default AdminDashboard;