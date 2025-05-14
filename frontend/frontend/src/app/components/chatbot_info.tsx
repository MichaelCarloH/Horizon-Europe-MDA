import React, { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import ReactMarkdown from "react-markdown"; // Import react-markdown
import remarkGfm from "remark-gfm"; // Import remark-gfm plugin

export function useIsVisible(ref: React.RefObject<HTMLDivElement>) {
  const [isIntersecting, setIntersecting] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIntersecting(entry.isIntersecting);
    });

    if (ref.current) {
      observer.observe(ref.current);
    }

    const refcurrent = ref.current;

    return () => {
      if (refcurrent) {
        observer.disconnect();
      }
    };
  }, [ref]);

  return isIntersecting;
}

const ChatbotInfo = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const paragraphRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);

  const headerVisible = useIsVisible(headerRef);
  const paragraphVisible = useIsVisible(paragraphRef);
  const imageVisible = useIsVisible(imageRef);
  const buttonVisible = useIsVisible(buttonRef);

  // Markdown content
  const markdownContent = `
  ## Chatbot with RAG Technology

  Our chatbot is powered by **Retrieval-Augmented Generation (RAG)**, a cutting-edge AI technology that combines **document retrieval** and **text generation** to provide highly relevant and human-like responses.

  The chatbot first retrieves the most relevant documents from a large database, ensuring that answers are based on **real-time, accurate information**. After retrieval, it generates coherent, natural language responses, helping users quickly access the knowledge they need.

  Whether you’re looking for **Horizon Europe funding information** or need to extract key insights from vast document sets, the RAG chatbot helps you find exactly what you’re looking for—**fast** and **efficiently**.
  `;

  return (
    <section className="text-gray-600 body-font mb-10">
      <div className="container mx-auto flex px-40 py-20 items-center justify-center flex-col lg:flex-row">
        <div className="lg:flex-grow md:w-1/2 lg:pr-24 md:pr-16 flex flex-col md:items-start md:text-left mb-16 md:mb-0 items-center text-center">
          <div
            ref={headerRef}
            className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
          >
            <h1 className="title-font sm:text-6xl text-4xl mb-4 font-medium text-gray-900">
              Chatbot with RAG Technology
            </h1>
          </div>
          <div
            ref={paragraphRef}
            className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
          >
            <div className="leading-relaxed py-5">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownContent}</ReactMarkdown>
            </div>
          </div>
        </div>
        <div
          ref={imageRef}
          className={`lg:max-w-lg lg:w-full md:w-1/2 w-5/6 shadow-xl bg-white rounded-3xl p-5 transition-opacity ease-in duration-2000 delay-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
        >
          <Image
            className="object-cover object-center border-2 border-blue-950 shadow-xl"
            alt="chatbot"
            width={500}  // Adjusted width to resize the image
            height={500} // Adjusted height to match the aspect ratio
            src={"/chatbot.png"} // Replace with your chatbot image
            style={{ borderRadius: "2rem" }}
          />
        </div>
      </div>
      <div
        ref={buttonRef}
        className={`flex justify-center mt-8 transition-opacity ease-in duration-700 delay-900 ${buttonVisible ? "opacity-100" : "opacity-0"}`}
      >
        <button className="inline-flex text-white bg-blue-950 border-0 py-5 px-12 focus:outline-none rounded-full text-lg shadow-xl">
          <Link href="./chatbot">Try the Chatbot</Link>
        </button>
      </div>
    </section>
  );
};

export default ChatbotInfo;
