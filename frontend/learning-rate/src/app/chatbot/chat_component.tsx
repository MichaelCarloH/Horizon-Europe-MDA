'use client'
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { FiSend, FiCopy, FiThumbsUp, FiThumbsDown } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
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
      // You could add a toast notification here
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
      const url = "http://localhost:8000/query";
      const payload = { text: query };
      
      const res = await axios.post(url, payload, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: 30000,
        withCredentials: false
      });

      const botResponse = res.data.answer;
      const sources = res.data.sources;
      
      let formattedResponse = botResponse;
      if (sources?.length > 0) {
        formattedResponse += "\n\n**Sources:**\n";
        sources.forEach((source: any, index: number) => {
          const metadata = source.metadata;
          formattedResponse += `\n${index + 1}. `;
          if (metadata.title) formattedResponse += `**Title:** ${metadata.title}\n`;
          if (metadata.projectID) formattedResponse += `**Project ID:** ${metadata.projectID}\n`;
          if (metadata.projectAcronym) formattedResponse += `**Acronym:** ${metadata.projectAcronym}\n`;
          formattedResponse += `**Relevance:** ${(source.relevance_score * 100).toFixed(1)}%\n`;
        });
      }

      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: "bot",
        text: formattedResponse,
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
        }
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
                      <p>{message.text}</p>
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
