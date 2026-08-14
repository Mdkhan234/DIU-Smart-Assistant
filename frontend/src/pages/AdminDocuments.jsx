import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function AdminDocuments() {

  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({
    total_documents: 0,
    total_pages: 0,
    total_chunks: 0,
  });

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState("");

  const fileInputRef = useRef(null);


  const loadDocuments = async () => {

    try {

      setLoading(true);

      const response = await api.get(
        "/admin/documents"
      );

      setDocuments(
        response.data.documents || []
      );

      setStats({
        total_documents:
          response.data.total_documents || 0,

        total_pages:
          response.data.total_pages || 0,

        total_chunks:
          response.data.total_chunks || 0,
      });

    } catch (error) {

      console.error(error);

      setMessage(
        "Unable to load documents."
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    loadDocuments();
  }, []);


  // ========================================================
  // UPLOAD
  // ========================================================

  const handleUpload = async (event) => {

    const file = event.target.files?.[0];

    if (!file) return;

    if (
      !file.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {

      setMessage(
        "Only PDF files are allowed."
      );

      event.target.value = "";
      return;
    }

    try {

      setUploading(true);
      setMessage("");

      const formData = new FormData();

      formData.append("file", file);

      const response = await api.post(
        "/upload",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      if (response.data.success) {

        setMessage(
          `${file.name} uploaded successfully.`
        );

        await loadDocuments();

      } else {

        setMessage(
          response.data.message ||
            "Upload failed."
        );
      }

    } catch (error) {

      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Failed to upload document."
      );

    } finally {

      setUploading(false);

      event.target.value = "";
    }
  };


  // ========================================================
  // DELETE
  // ========================================================

  const handleDelete = async (filename) => {

    const confirmed = window.confirm(
      `Delete "${filename}"?\n\nThe knowledge base will also be rebuilt.`
    );

    if (!confirmed) return;

    try {

      setMessage("");

      const encodedFilename =
        encodeURIComponent(filename);

      const response = await api.delete(
        `/admin/documents/${encodedFilename}`
      );

      if (response.data.success) {

        setMessage(
          `"${filename}" deleted successfully.`
        );

        await loadDocuments();
      }

    } catch (error) {

      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Failed to delete document."
      );
    }
  };


  // ========================================================
  // REBUILD
  // ========================================================

  const handleRebuild = async () => {

    try {

      setRebuilding(true);
      setMessage("");

      const response = await api.post(
        "/admin/rebuild-vector-db"
      );

      if (response.data.success) {

        const details =
          response.data.details;

        setMessage(
          `Knowledge base rebuilt: ${details.documents} documents, ${details.pages} pages, ${details.chunks} chunks.`
        );

        await loadDocuments();
      }

    } catch (error) {

      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Failed to rebuild knowledge base."
      );

    } finally {

      setRebuilding(false);
    }
  };


  const formatSize = (bytes) => {

    if (!bytes) return "—";

    const mb = bytes / 1024 / 1024;

    if (mb >= 1) {
      return `${mb.toFixed(2)} MB`;
    }

    return `${(bytes / 1024).toFixed(1)} KB`;
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
          to="/admin"
          className="admin-back-button"
        >
          ← Dashboard
        </Link>

      </header>


      {/* Main */}

      <main className="admin-content">

        <div className="admin-title-section">

          <div>

            <span className="admin-eyebrow">
              KNOWLEDGE BASE
            </span>

            <h2>Documents</h2>

            <p>
              Manage the PDFs used by the AI assistant.
            </p>

          </div>


          <div className="document-toolbar">

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleUpload}
              hidden
            />

            <button
              className="upload-button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "+ Upload PDF"}
            </button>


            <button
              className="rebuild-button secondary"
              onClick={handleRebuild}
              disabled={rebuilding}
            >
              {rebuilding
                ? "Rebuilding..."
                : "↻ Rebuild"}
            </button>

          </div>

        </div>


        {/* Stats */}

        <div className="mini-stats">

          <div>
            <span>Documents</span>
            <strong>
              {stats.total_documents}
            </strong>
          </div>

          <div>
            <span>Pages</span>
            <strong>
              {stats.total_pages}
            </strong>
          </div>

          <div>
            <span>Chunks</span>
            <strong>
              {stats.total_chunks}
            </strong>
          </div>

        </div>


        {/* Notification */}

        {message && (
          <div className="admin-notification">
            {message}
          </div>
        )}


        {/* Documents */}

        <section className="documents-panel">

          <div className="documents-panel-header">

            <div>
              <h3>Uploaded Documents</h3>

              <p>
                {documents.length} PDF
                {documents.length !== 1
                  ? "s"
                  : ""}{" "}
                in the knowledge base
              </p>
            </div>

          </div>


          {loading ? (

            <div className="documents-empty">
              <div className="loading-spinner"></div>
              <p>Loading documents...</p>
            </div>

          ) : documents.length === 0 ? (

            <div className="documents-empty">

              <div className="empty-icon">
                📄
              </div>

              <h3>No documents yet</h3>

              <p>
                Upload a PDF to start building the knowledge base.
              </p>

            </div>

          ) : (

            <div className="documents-list">

              {documents.map((document) => (

                <div
                  className="document-row"
                  key={document.filename}
                >

                  <div className="document-file-icon">
                    PDF
                  </div>


                  <div className="document-info">

                    <h4>
                      {document.filename}
                    </h4>

                    <div className="document-meta">

                      <span>
                        {formatSize(
                          document.size_bytes
                        )}
                      </span>

                      <span>
                        {document.pages} pages
                      </span>

                      <span>
                        {document.chunks} chunks
                      </span>

                    </div>

                  </div>


                  <div className="document-status">

                    <span
                      className={
                        document.status === "Indexed"
                          ? "status-badge indexed"
                          : "status-badge error"
                      }
                    >
                      ● {document.status}
                    </span>

                  </div>


                  <button
                    className="delete-button"
                    onClick={() =>
                      handleDelete(
                        document.filename
                      )
                    }
                    title="Delete document"
                  >
                    🗑
                  </button>

                </div>

              ))}

            </div>

          )}

        </section>

      </main>

    </div>
  );
}

export default AdminDocuments;