import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

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
    <div className="h-screen flex flex-col justify-center items-center bg-gray-100 p-6">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-md p-6 space-y-4 overflow-auto">
        <h1 className="text-3xl font-semibold text-center text-gray-800 mb-4">Ask the AI Chatbot</h1>
        
        <div className="flex flex-col space-y-4">
          {/* Input Field */}
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder="Ask a question"
            className="p-3 border border-blue-400 rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-500 text-white p-3 rounded-md hover:bg-blue-600 transition"
          >
            {loading ? "Processing..." : "Submit"}
          </button>

          {/* Error Message */}
          {error && <div className="text-red-500 text-center">{error}</div>}

          <div className="mt-4 space-y-4">
            {/* Query Display */}
            <div className="query-container flex items-center space-x-2">
              <span className="text-lg font-medium text-gray-700">Your Query:</span>
              <p className="bg-blue-100 p-3 rounded-lg text-blue-600 shadow-md">{query}</p>
            </div>

            {/* Response Display */}
            {response && (
              <div className="mt-4 p-4 bg-gray-100 rounded-md shadow-md h-64 overflow-y-auto">
                <h2 className="font-semibold text-xl mb-2">Response:</h2>
                <ReactMarkdown
                  children={response} // Passing the raw markdown content
                  components={{
                    h1: ({ children }) => <h1 className="text-3xl font-bold text-blue-600">{children}</h1>,
                    p: ({ children }) => <p className="text-lg text-gray-700">{children}</p>,
                    code: ({ children }) => <code className="bg-gray-200 p-1 rounded">{children}</code>,
                    // You can add more custom renderers for markdown elements here
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;
