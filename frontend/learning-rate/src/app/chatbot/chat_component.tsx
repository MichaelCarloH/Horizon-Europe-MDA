'use client'
import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const ChatComponent = () => {
  const [query, setQuery] = useState(""); // For user input
  const [messages, setMessages] = useState<{ sender: string, text: string }[]>([]); // To store the conversation history
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async () => {
    if (!query) return;

    // Add user's message to the chat
    setMessages((prevMessages) => [...prevMessages, { sender: "user", text: query }]);

    setLoading(true);
    setError(null);
    try {
      //const url = "https://mda-horizon-backend-2025.azurewebsites.net/query";
      const url = "http://localhost:8000/query";
      const payload = { text: query };
      const headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://horizon-europe-mda.vercel.app',
        'Accept': 'application/json'
      };

      console.log('Request details:', {
        url,
        payload,
        headers
      });

      const res = await axios.post(url, payload, {
        headers,
        timeout: 10000, // 10 second timeout
        withCredentials: false // Don't send cookies
      });

      console.log('Response details:', {
        status: res.status,
        headers: res.headers,
        data: res.data
      });

      const botResponse = res.data.answer;
      const sources = res.data.sources;
      
      // Format the response with sources
      let formattedResponse = botResponse;
      if (sources && sources.length > 0) {
        formattedResponse += "\n\nSources:\n";
        sources.forEach((source: any, index: number) => {
          const metadata = source.metadata;
          formattedResponse += `\n${index + 1}. `;
          if (metadata.title) formattedResponse += `Title: ${metadata.title}\n`;
          if (metadata.projectID) formattedResponse += `Project ID: ${metadata.projectID}\n`;
          if (metadata.projectAcronym) formattedResponse += `Acronym: ${metadata.projectAcronym}\n`;
          formattedResponse += `Relevance: ${(source.relevance_score * 100).toFixed(1)}%\n`;
        });
      }

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: formattedResponse },
      ]);
    } catch (err) {
      console.error('Full error:', err);
      if (axios.isAxiosError(err)) {
        if (err.code === 'ECONNABORTED') {
          setError('Request timed out. Please try again.');
        } else if (err.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error('Error response:', {
            status: err.response.status,
            statusText: err.response.statusText,
            headers: err.response.headers,
            data: err.response.data
          });
          setError(`Server error: ${err.response.status} - ${err.response.data?.detail || err.message}`);
        } else if (err.request) {
          // The request was made but no response was received
          console.error('No response received:', {
            request: err.request,
            message: err.message
          });
          setError('No response from server. Please check your connection.');
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error('Request setup error:', err.message);
          setError(`Error: ${err.message}`);
        }
      } else {
        console.error('Unexpected error:', err);
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }

    setQuery(""); // Clear the input field after sending the query
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', alignItems: 'center', backgroundColor: '#f7fafc', padding: '1.5rem' }}>
      {/* Fixed Header */}
      <div style={{ position: 'sticky', top: 0, width: '100%', backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.375rem', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', zIndex: 10 }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '600', textAlign: 'center', color: '#2d3748' }}>Ask the AI Chatbot</h1>
      </div>

      {/* Chat Messages and Input Area */}
      <div style={{ maxWidth: '100%', width: '100%', backgroundColor: 'white', borderRadius: '0.375rem', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', padding: '1.5rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/* Chat Messages Section */}
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
          {messages.map((message, index) => (
            <div key={index} style={{ display: 'flex', justifyContent: message.sender === "user" ? 'flex-end' : 'flex-start' }}>
              <div
                style={{
                  padding: '1rem',
                  maxWidth: '80%',
                  borderRadius: '0.375rem',
                  backgroundColor: message.sender === "user" ? '#bee3f8' : '#edf2f7',
                  color: message.sender === "user" ? '#3182ce' : '#2d3748',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                }}
              >
                {message.sender === "user" ? (
                  <p style={{ fontWeight: '500' }}>{message.text}</p>
                ) : (
                  <div style={{ fontSize: '1rem', color: '#2d3748' }}>
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input Field and Button */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder="Ask a question"
            className="p-3 border border-blue-400 rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />

          <button
            onClick={handleSubmit}
            disabled={loading}
            style={{
              backgroundColor: '#3182ce',
              color: 'white',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              transition: 'background-color 0.3s',
            }}
          >
            {loading ? "Processing..." : "Submit"}
          </button>

          {error && <div style={{ color: '#e53e3e', textAlign: 'center' }}>{error}</div>}
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;
