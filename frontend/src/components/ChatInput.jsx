function ChatInput({
  input,
  setInput,
  onSend,
  loading,
}) {
  const handleKeyDown = (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      onSend();
    }
  };

  return (
    <div className="chat-input-area">

      <div className="chat-input-box">

        <textarea
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about Daffodil International University..."
          rows={1}
          disabled={loading}
        />

        <button
          className="chat-send-button"
          onClick={onSend}
          disabled={
            !input.trim() || loading
          }
        >
          {loading ? (
            <span className="send-loading">
              ...
            </span>
          ) : (
            "➤"
          )}
        </button>

      </div>

      <div className="chat-input-hint">
        AI can make mistakes. Verify important information.
      </div>

    </div>
  );
}

export default ChatInput;