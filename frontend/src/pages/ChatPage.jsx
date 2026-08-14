import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import api from "../api";

function createSessionId() {
  return `web-${Date.now()}-${Math.random()
    .toString(36)
    .substring(2, 9)}`;
}

function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! 👋 I'm **DIU Smart Assistant**.\n\nAsk me anything about **Daffodil International University**.",
      sources: [],
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const sessionId = useRef(createSessionId());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const autoResize = () => {
    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height =
      Math.min(textarea.scrollHeight, 140) + "px";
  };

  const sendMessage = async () => {
    const question = input.trim();

    if (!question || loading) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
        sources: [],
      },
    ]);

    setInput("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    setLoading(true);

    try {
      const response = await api.post("/chat", {
        session_id: sessionId.current,
        question,
      });

      const data = response.data;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data.answer ||
            "Sorry, I could not generate an answer.",
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the DIU Smart Assistant server. Please make sure the FastAPI backend is running.",
          sources: [],
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    sessionId.current = createSessionId();

    setMessages([
      {
        role: "assistant",
        content:
          "Hello! 👋 I'm **DIU Smart Assistant**.\n\nAsk me anything about **Daffodil International University**.",
        sources: [],
      },
    ]);

    setInput("");

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 50);
  };

  return (
    <div className="chat-page">

      {/* HEADER */}
      <header className="chat-header">
        <div className="chat-brand">

          <div className="chat-logo">
            DIU
          </div>

          <div className="chat-brand-text">
            <h1>DIU Smart Assistant</h1>
            <p>University information assistant</p>
          </div>

        </div>

        <button
          className="new-chat-button"
          onClick={clearChat}
          disabled={loading}
        >
          <span className="plus-icon">+</span>
          <span>New Chat</span>
        </button>
      </header>


      {/* CHAT */}
      <main className="chat-main">

        <div className="chat-messages">

          {messages.map((message, index) => {
            const isUser = message.role === "user";

            return (
              <div
                key={index}
                className={`chat-message-row ${
                  isUser ? "user-message" : "assistant-message"
                }`}
              >

                {/* Avatar */}
                <div
                  className={`chat-avatar ${
                    isUser ? "user-avatar" : "assistant-avatar"
                  }`}
                >
                  {isUser ? "U" : "AI"}
                </div>


                {/* Message */}
                <div className="chat-message-content">

                  <div className="chat-message-name">
                    {isUser ? "You" : "DIU Assistant"}
                  </div>


                  <div
                    className={`chat-bubble ${
                      message.error ? "chat-error" : ""
                    }`}
                  >

                    {isUser ? (
                      <div className="plain-message">
                        {message.content}
                      </div>
                    ) : (
                      <div className="markdown-message">
                        <ReactMarkdown>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    )}

                  </div>


                  {/* SOURCES */}
                  {!isUser &&
                    message.sources &&
                    message.sources.length > 0 && (

                      <div className="chat-sources">

                        <div className="sources-heading">
                          <span className="sources-icon">
                            ▣
                          </span>

                          <span>
                            Sources
                          </span>
                        </div>


                        <div className="sources-list">

                          {message.sources.map(
                            (source, sourceIndex) => (
                              <div
                                className="source-card"
                                key={sourceIndex}
                              >

                                <div className="source-document-icon">
                                  PDF
                                </div>

                                <div className="source-details">

                                  <div className="source-filename">
                                    {String(
                                      source.filename || ""
                                    ).replace(
                                      /^data[\\/]+uploads[\\/]+/,
                                      ""
                                    )}
                                  </div>

                                  <div className="source-meta">
                                    Page{" "}
                                    {Number(source.page || 0) + 1}
                                  </div>

                                </div>

                              </div>
                            )
                          )}

                        </div>

                      </div>
                    )}

                </div>

              </div>
            );
          })}


          {/* TYPING */}
          {loading && (
            <div className="chat-message-row assistant-message">

              <div className="chat-avatar assistant-avatar">
                AI
              </div>

              <div className="chat-message-content">

                <div className="chat-message-name">
                  DIU Assistant
                </div>

                <div className="chat-bubble typing-bubble">

                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>

                </div>

              </div>

            </div>
          )}

          <div ref={messagesEndRef} />

        </div>

      </main>


      {/* INPUT */}
      <footer className="chat-input-area">

        <div className="chat-input-container">

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(event) => {
              setInput(event.target.value);
              autoResize();
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about Daffodil International University..."
            rows={1}
            disabled={loading}
          />

          <button
            className="chat-send-button"
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            aria-label="Send message"
          >
            {loading ? (
              <span className="send-loading">
                •••
              </span>
            ) : (
              <span className="send-arrow">
                ↑
              </span>
            )}
          </button>

        </div>


        <div className="chat-input-hint">
          <span>Enter</span> to send
          <span className="hint-dot">•</span>
          <span>Shift + Enter</span> for a new line
        </div>

      </footer>

    </div>
  );
}

export default ChatPage;