// src/app/chatbot/page.tsx
'use client'
import ChatComponent from "@/app/components/chat_component";  // Importing the chatbot component

export default function ChatbotPage() {
  return (
    <main className="p-6">
      <h1 className="text-4xl font-bold text-center mb-8">Chat with Our AI Bot!</h1>
      <ChatComponent />
    </main>
  );
}
