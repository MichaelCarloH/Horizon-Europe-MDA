'use client'
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { FiSend, FiCopy, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import { API_CONFIG, QueryResponse, formatResponse } from '../config/api';
import './chat.css';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
  feedback?: 'like' | 'dislike';
}

interface CodeProps {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const ChatComponent = () => {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: 'welcome',
        sender: 'bot',
        text: `Welcome! I'm your Horizon Europe project assistant. I can help you navigate funding opportunities and project management.

For detailed information, visit the [official Horizon Europe portal](https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en).

What would you like to know about Horizon Europe?`,
        timestamp: new Date()
      }]);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleFeedback = (messageId: string, feedback: 'like' | 'dislike') => {
    setMessages(messages.map(msg => 
      msg.id === messageId ? { ...msg, feedback } : msg
    ));
  };

  const handleSubmit = async () => {
    if (!query.trim() || loading) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: query.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setLoading(true);
    setIsTyping(true);
    setError(null);

    try {
      const { BASE_URL, ENDPOINTS, TIMEOUT, HEADERS } = API_CONFIG.CHAT;
      const url = `${BASE_URL}${ENDPOINTS.QUERY}`;
      
      const res = await axios.post<QueryResponse>(url, { 
        text: query,
        context: "This is a Horizon Europe project assistant. Please provide responses relevant to Horizon Europe funding, project management, and related topics."
      }, {
        headers: HEADERS,
        timeout: TIMEOUT,
        withCredentials: false
      });

      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: "bot",
        text: formatResponse(res.data),
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('Error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
      setIsTyping(false);
      setQuery("");
    }
  };

  const renderMarkdown = (text: string) => (
    <ReactMarkdown
      components={{
        code: ({ node, inline, className, children, ...props }: CodeProps) => {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <div className="relative group">
              <button
                onClick={() => copyToClipboard(String(children))}
                className="absolute top-2 right-2 p-2 rounded bg-gray-700 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Copy code"
              >
                <FiCopy className="text-white" />
              </button>
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
        h1: ({ children }) => <h1 className="text-2xl font-bold mb-4 mt-6">{children}</h1>,
        h2: ({ children }) => <h2 className="text-xl font-bold mb-3 mt-5">{children}</h2>,
        h3: ({ children }) => <h3 className="text-lg font-bold mb-2 mt-4">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>,
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50">
            {children}
          </blockquote>
        ),
        a: ({ href, children }) => (
          <a 
            href={href} 
            className="text-blue-600 hover:text-blue-800 underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            {children}
          </a>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full divide-y divide-gray-200">
              {children}
            </table>
          </div>
        ),
        th: ({ children }) => (
          <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {children}
          </td>
        ),
        hr: () => <hr className="my-6 border-gray-200" />,
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
      }}
    >
      {text}
    </ReactMarkdown>
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen max-w-5xl mx-auto">
        <div className="flex-1 flex flex-col bg-white shadow-lg relative h-full">
          {/* Header */}
          <div className="p-4 border-b bg-white sticky top-0 z-10">
            <h1 className="text-xl font-semibold text-gray-800">AI Assistant</h1>
          </div>

          {/* Messages Container */}
          <div 
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
            style={{ 
              height: 'calc(100vh - 180px)',
              backgroundImage: 'radial-gradient(circle at center, #f3f4f6 1px, transparent 1px)',
              backgroundSize: '24px 24px'
            }}
          >
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 shadow-sm ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border'
                    }`}
                  >
                    {message.sender === 'user' ? (
                      <p className="whitespace-pre-wrap">{message.text}</p>
                    ) : (
                      <div className="prose dark:prose-invert max-w-none">
                        {renderMarkdown(message.text)}
                        <div className="flex items-center space-x-2 mt-2 message-feedback">
                          <button
                            onClick={() => handleFeedback(message.id, 'like')}
                            className={`p-1 rounded hover:bg-gray-100 ${
                              message.feedback === 'like' ? 'text-green-500' : 'text-gray-400'
                            }`}
                          >
                            <FiThumbsUp />
                          </button>
                          <button
                            onClick={() => handleFeedback(message.id, 'dislike')}
                            className={`p-1 rounded hover:bg-gray-100 ${
                              message.feedback === 'dislike' ? 'text-red-500' : 'text-gray-400'
                            }`}
                          >
                            <FiThumbsDown />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-2 text-gray-500"
                >
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="border-t bg-white p-4 sticky bottom-0 z-10">
            {error && (
              <div className="text-red-500 mb-2 text-center">{error}</div>
            )}
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                handleSubmit();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={query}
                onChange={handleQueryChange}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <FiSend className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;
