import React, { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";

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

const PGInfo = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const paragraphRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);

  const headerVisible = useIsVisible(headerRef);
  const paragraphVisible = useIsVisible(paragraphRef);
  const imageVisible = useIsVisible(imageRef);
  const buttonVisible = useIsVisible(buttonRef);

  return (
    <section className="text-gray-600 body-font">
      <div className="container mx-auto flex px-5 py-20 items-center justify-center flex-col">
        <div className="text-center lg:w-2/3 w-full">
          <div
            ref={headerRef}
            className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
          >
            <h1 className="title-font sm:text-6xl text-4xl mb-4 font-medium text-gray-900">
              Implement with the Playground
            </h1>
          </div>
          <div
            ref={paragraphRef}
            className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
          >
            <p className="leading-relaxed py-5">
              The playground is an interactive platform designed to provide a
              visual understanding of neural networks. Users can intuitively drag
              and drop neurons onto the playground canvas and connect them to
              create neural networks. As neurons are connected, users can observe
              real-time changes in the network&apos;s behavior. This interactive
              experience facilitates learning about neural network architecture
              and connectivity in an engaging and accessible manner.
            </p>
          </div>
          <div
            ref={imageRef}
            className={`flex justify-center py-10  overflow-hidden transition-opacity ease-in duration-2000 delay-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
          >
            <Image
              className="object-cover object-center border-2 border-blue-950 shadow-xl"
              alt="hero"
              width={2000}
              height={500}
              src={"/playground_mainpage.png"}
              style={{ borderRadius: "2rem" }} // Adjust the border-radius as desired
            />
          </div>
          <div 
            ref={buttonRef}
            className={`flex justify-center mt-8 transition-opacity ease-in duration-700 delay-900 ${buttonVisible ? "opacity-100" : "opacity-0"}`}
          >
            <button className="inline-flex text-white bg-blue-950 border-0 py-5 px-12 focus:outline-none rounded-full text-lg shadow-xl">
              <Link href="./playground">Go to Playground</Link>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
          
export default PGInfo;
          
