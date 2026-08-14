import { useEffect, useRef, useState } from "react";
import api from "../api";

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState("");

  const fileInputRef = useRef(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);

      const response = await api.get("/admin/documents");

      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error(error);
      setMessage("Failed to load documents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const uploadDocument = async (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setMessage("Only PDF files are allowed.");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {
      setUploading(true);
      setMessage("");

      const response = await api.post(
        "/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (response.data.success) {
        setMessage(
          response.data.message ||
            "PDF uploaded successfully."
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
          "Failed to upload PDF."
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const deleteDocument = async (filename) => {

    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    try {

      setMessage("");

      await api.delete(
        `/admin/documents/${encodeURIComponent(filename)}`
      );

      setMessage(
        "Document deleted successfully."
      );

      await loadDocuments();

    } catch (error) {

      console.error(error);

      setMessage(
        error.response?.data?.detail ||
          "Failed to delete document."
      );
    }
  };

  const rebuildDatabase = async () => {

    const confirmed = window.confirm(
      "Rebuild the entire knowledge base?"
    );

    if (!confirmed) {
      return;
    }

    try {

      setRebuilding(true);
      setMessage("");

      const response = await api.post(
        "/admin/rebuild"
      );

      if (response.data.success) {

        setMessage(
          `Knowledge base rebuilt successfully. ${response.data.total_chunks} chunks indexed.`
        );

        await loadDocuments();

      } else {

        setMessage(
          response.data.message ||
            "Rebuild failed."
        );
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

    if (!bytes) {
      return "0 KB";
    }

    const mb = bytes / (1024 * 1024);

    if (mb >= 1) {
      return `${mb.toFixed(1)} MB`;
    }

    return `${Math.max(
      1,
      Math.round(bytes / 1024)
    )} KB`;
  };

  return (
    <div className="documents-page">

      <div className="documents-header">

        <div>
          <h2>Documents</h2>

          <p>
            Manage the documents used by the DIU
            Smart Assistant.
          </p>
        </div>

        <div className="document-actions">

          <button
            className="secondary-button"
            onClick={rebuildDatabase}
            disabled={rebuilding || uploading}
          >
            {rebuilding
              ? "Rebuilding..."
              : "Rebuild Knowledge Base"}
          </button>

          <button
            className="primary-button"
            onClick={() =>
              fileInputRef.current?.click()
            }
            disabled={uploading}
          >
            {uploading
              ? "Uploading..."
              : "+ Upload PDF"}
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={uploadDocument}
            hidden
          />

        </div>
      </div>

      {message && (
        <div className="admin-message">
          {message}
        </div>
      )}

      <div className="document-card">

        {loading ? (

          <div className="empty-state">
            Loading documents...
          </div>

        ) : documents.length === 0 ? (

          <div className="empty-state">

            <div className="empty-icon">
              📄
            </div>

            <h3>No documents yet</h3>

            <p>
              Upload a PDF to add knowledge to
              the assistant.
            </p>

          </div>

        ) : (

          <div className="document-table-wrapper">

            <table className="document-table">

              <thead>
                <tr>
                  <th>Document</th>
                  <th>Pages</th>
                  <th>Chunks</th>
                  <th>Size</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {documents.map((document) => (

                  <tr key={document.filename}>

                    <td>

                      <div className="document-name">

                        <div className="pdf-icon">
                          PDF
                        </div>

                        <div>
                          <strong>
                            {document.filename}
                          </strong>

                          <small>
                            PDF Document
                          </small>
                        </div>

                      </div>

                    </td>

                    <td>
                      {document.pages}
                    </td>

                    <td>
                      {document.chunks}
                    </td>

                    <td>
                      {formatSize(
                        document.size
                      )}
                    </td>

                    <td>

                      <span
                        className={
                          document.status ===
                          "Indexed"
                            ? "status-badge success"
                            : "status-badge error"
                        }
                      >
                        ● {document.status}
                      </span>

                    </td>

                    <td>

                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteDocument(
                            document.filename
                          )
                        }
                      >
                        Delete
                      </button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}

export default Documents;