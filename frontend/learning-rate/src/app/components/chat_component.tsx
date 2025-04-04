// pages/index.tsx (or a new component)

import { useState } from "react";
import axios from "axios";

const ChatComponent = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async () => {
    if (!query) return;

    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:8000/query/", {
        query_text: query,
        k: 3, // You can customize this if you want
      });
      setResponse(res.data.response);  // Assuming the backend sends a response field
    } catch (err) {
      setError("Error processing query.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>LLM Query Chatbot</h1>
      <input
        type="text"
        value={query}
        onChange={handleQueryChange}
        placeholder="Ask a question"
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Submit"}
      </button>

      {error && <div style={{ color: "red" }}>{error}</div>}

      {response && (
        <div>
          <h2>Response:</h2>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default ChatComponent;
