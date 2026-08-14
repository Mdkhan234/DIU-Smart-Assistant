function Sidebar({
  chats,
  activeChat,
  onNewChat,
  onSelectChat,
}) {
  return (
    <aside className="sidebar">

      <div className="sidebar-top">

        <div className="sidebar-brand">
          <div className="sidebar-logo">
            DIU
          </div>

          <div>
            <h2>DIU Assistant</h2>
            <span>University AI Assistant</span>
          </div>
        </div>

        <button
          className="new-chat-button"
          onClick={onNewChat}
        >
          <span>＋</span>
          New Chat
        </button>

      </div>

      <div className="chat-history">

        <div className="history-title">
          Recent Chats
        </div>

        {chats.length === 0 ? (

          <div className="empty-history">
            No conversations yet.
          </div>

        ) : (

          chats.map((chat) => (

            <button
              key={chat.id}
              className={`history-item ${
                activeChat === chat.id ? "active" : ""
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <span className="history-icon">
                💬
              </span>

              <span className="history-text">
                {chat.title}
              </span>
            </button>

          ))

        )}

      </div>

      <div className="sidebar-bottom">

        <div className="assistant-status">

          <span className="status-dot"></span>

          <div>
            <strong>DIU AI</strong>
            <span>Online</span>
          </div>

        </div>

        <div className="sidebar-footer">
          Powered by RAG
        </div>

      </div>

    </aside>
  );
}

export default Sidebar;