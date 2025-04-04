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

const Hero = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const paragraphRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  const headerVisible = useIsVisible(headerRef);
  const paragraphVisible = useIsVisible(paragraphRef);
  const buttonVisible = useIsVisible(buttonRef);
  const imageVisible = useIsVisible(imageRef);

  return (
    <section className="body-font bg-sky-700">
      <div className="container mx-auto flex px-40 py-20 md:flex-row flex-col items-center">
        <div className="lg:flex-grow md:w-1/2 lg:pr-24 md:pr-16 flex flex-col md:items-start md:text-left mb-16 md:mb-0 items-center text-center">
          <div
            ref={headerRef}
            className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
          >
            <h1 className="title-font sm:text-5xl text-3xl text-white mb-4 font-medium">
              Your gateway to understanding neural networks
            </h1>
          </div>
          <div
            ref={paragraphRef}
            className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
          >
            <p className="mb-8 leading-relaxed text-white">
              Learning Rate is an educational website designed to teach
              beginners how neural networks work. Whether you&apos;re new to the
              concept or looking to deepen your understanding, we&apos;ve got you
              covered. Dive into the world of artificial intelligence and
              discover the magic behind neural networks.
            </p>
          </div>
          <div
            ref={buttonRef}
            className={`transition-opacity ease-in duration-700 delay-600 ${buttonVisible ? "opacity-100" : "opacity-0"}`}
          >
            <div className="flex justify-center">
              <button className="inline-flex text-white bg-blue-950 border-0 py-2 px-6 focus:outline-none rounded text-lg shadow-xl">
                <Link href="./about">More info</Link>
              </button>
            </div>
          </div>
        </div>
        <div
          ref={imageRef}
          className={`lg:max-w-lg lg:w-full md:w-1/2 w-5/6 shadow-xl bg-white rounded-3xl p-5 transition-opacity ease-in duration-2000 delay-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
        >
          <Image
            src={"/NeurNet.png"}
            alt="hero"
            width={720}
            height={600}
            className="object-cover object-center rounded"
          />
        </div>
      </div>
    </section>
  );
};

export default Hero;
