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

const DataScienceProjects = () => {
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

  Our data science projects provide a **comprehensive overview** of Horizon Europe projects so that you can understand the latest trends and developments in the program using **intuitive and interactive** visualizations and dashboards.
  

  With the use of modern data science techniques, our projects cover topics such as fundings by organizations, trends in research areas, and the impact of Horizon Europe projects on various sectors - allowing you to **stay informed** about the **latest developments** in the billion-euro initiative by the EU.
  
  
  `;

  return (
    <section className="text-gray-600 body-font mb-10">
      <div className="container mx-auto flex px-40 py-20 items-center justify-center flex-col lg:flex-row">
        <div className="lg:flex-grow md:w-1/2 lg:pr-24 md:pr-16 flex flex-col md:items-start md:text-left mb-16 md:mb-0 items-center text-center">
          <div
            ref={headerRef}
            className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
          >
            <h1 className="title-font sm:text-5xl text-3xl mb-4 font-medium text-gray-900">
              Data Science Projects
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
            alt="projects"
            width={500}  // Adjusted width to resize the image
            height={500} // Adjusted height to match the aspect ratio
            src={"/ds-project-about.jpg"} // Replace with your chatbot image
            style={{ borderRadius: "2rem" }}
          />
        </div>
      </div>
      <div
        ref={buttonRef}
        className={`flex justify-center mt-8 transition-opacity ease-in duration-700 delay-900 ${buttonVisible ? "opacity-100" : "opacity-0"}`}
      >
        <button className="inline-flex text-white bg-blue-950 border-0 py-3 px-8 focus:outline-none rounded-full text-base shadow-xl">
          <Link href="./projects">Check out our projects</Link>
        </button>
      </div>
    </section>
  );
};

export default DataScienceProjects;
