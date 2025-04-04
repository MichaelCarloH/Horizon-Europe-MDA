'use client'
import Hero from "@/app/components/hero";
import PGInfo from "@/app/components/playground_info";
import LessonsInfo from "@/app/components/lessons_info";
import ChatComponent from "@/app/components/chat_component";

export default function Home() {
  return (
    <main>
      <Hero />
      <PGInfo />
      <ChatComponent />
      <LessonsInfo />
    </main>
  );
};
