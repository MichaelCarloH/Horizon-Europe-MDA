// src/app/components/chat_component.tsx
'use client'
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
    <div className="max-w-md mx-auto p-6 border rounded-lg shadow-md bg-white">
      <h1 className="text-2xl font-semibold text-center mb-4">Ask the AI Chatbot</h1>
      
      <div className="flex flex-col space-y-4">
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Ask a question"
          className="p-2 border border-gray-300 rounded"
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition"
        >
          {loading ? "Processing..." : "Submit"}
        </button>

        {error && <div className="text-red-500 text-center">{error}</div>}

        {response && (
          <div className="mt-4 p-4 bg-gray-100 rounded-md">
            <h2 className="font-semibold">Response:</h2>
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatComponent;
