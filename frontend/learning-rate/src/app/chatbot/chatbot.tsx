import { useState } from "react";
import axios from "axios";

const ChatbotPage = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async () => {
    if (!query) return;

    // Add user message to chat
    setMessages([...messages, { user: query, bot: "..." }]);
    setLoading(true);
    setError(null);
    
    try {
      const res = await axios.post("http://localhost:8000/query/", {
        query_text: query,
        k: 3,
      });
      setResponse(res.data.response);
      // Add bot response to chat
      setMessages([
        ...messages,
        { user: query, bot: res.data.response },
      ]);
    } catch (err) {
      setError("Error processing query.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <h1>Chat with Our AI</h1>
      <div className="chatbox">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.user ? "user" : "bot"}`}>
              <span>{msg.user ? `You: ${msg.user}` : `Bot: ${msg.bot}`}</span>
            </div>
          ))}
        </div>
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Ask a question..."
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Processing..." : "Send"}
        </button>
      </div>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
};

export default ChatbotPage;