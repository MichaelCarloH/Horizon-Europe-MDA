'use client'
import Hero from "@/app/components/hero";
import ChatbotInfo from "@/app/components/chatbot_info";
import DataScienceProjects from "./components/ds_projects";

export default function Home() {
  return (
    <main>
      <Hero />
      <ChatbotInfo />
      <DataScienceProjects />
    </main>
  );
};