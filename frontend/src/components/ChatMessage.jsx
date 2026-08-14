function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`chat-message-row ${
        isUser ? "user-message" : "assistant-message"
      }`}
    >

      <div className="chat-avatar">
        {isUser ? "👤" : "🤖"}
      </div>

      <div className="chat-message-content">

        <div className="chat-message-name">
          {isUser ? "You" : "DIU Assistant"}
        </div>

        <div
          className={`chat-bubble ${
            message.error ? "error" : ""
          }`}
        >
          {message.content}
        </div>

        {message.sources &&
          message.sources.length > 0 && (

            <div className="message-sources">

              <div className="sources-heading">
                📚 Sources
              </div>

              {message.sources.map(
                (source, index) => (

                  <div
                    className="message-source"
                    key={index}
                  >

                    <span>
                      📄 {source.filename}
                    </span>

                    <span>
                      Page {source.page}
                    </span>

                  </div>

                )
              )}

            </div>

          )}

      </div>

    </div>
  );
}

export default ChatMessage;