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

const LessonsInfo = () => {
  const headerRef = useRef<HTMLDivElement>(null);
  const paragraphRef = useRef<HTMLDivElement>(null);
  const image1Ref = useRef<HTMLDivElement>(null);
  const image2Ref = useRef<HTMLDivElement>(null);
  const image3Ref = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);

  const headerVisible = useIsVisible(headerRef);
  const paragraphVisible = useIsVisible(paragraphRef);
  const image1Visible = useIsVisible(image1Ref);
  const image2Visible = useIsVisible(image2Ref);
  const image3Visible = useIsVisible(image3Ref);
  const buttonVisible = useIsVisible(buttonRef);

  return (
    <section className="text-gray-600 body-font">
      <div className="container px-5 py-10 mx-auto">
        <div className="flex flex-col text-center w-full mb-10">
          <div
            ref={headerRef}
            className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
          >
            <h1 className="sm:text-6xl text-4xl font-medium title-font mb-4 text-gray-900">
              Learn with Interactive Lessons
            </h1>
          </div>
          <div
            ref={paragraphRef}
            className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
          >
            <p className="lg:w-2/3 mx-auto leading-relaxed text-base py-5">
              Embark on an interactive journey through the intricacies of neural
              networks on our educational platform. Our engaging lessons not only
              simplify complex concepts but also offer interactive experiences,
              allowing you to actively participate in your learning. From
              understanding AI neurons and activation functions to delving into
              Multi-Layer Perceptrons (MLPs) and backpropagation, our interactive
              approach ensures an engaging and immersive learning experience.
            </p>
          </div>
        </div>
        <div className="container px-5 mx-auto">
          <div className="flex flex-wrap sm:-m-4 -mx-4 -mb-10 -mt-4">
            <div
              ref={image1Ref}
              className={`p-4 md:w-1/3 sm:mb-0 mb-6 transition-opacity ease-in duration-2000 delay-600 ${image1Visible ? "opacity-100" : "opacity-0"}`}
            >
              <div className="rounded-3xl h-64 overflow-hidden shadow-2xl border-2 border-blue-950">
                <Image
                  alt="content"
                  className="object-cover object-center h-full w-full  shadow-2xl"
                  src={"/lesson1_mainpage.png"}
                  width={1203}
                  height={503}
                />
              </div>
            </div>
            <div
              ref={image2Ref}
              className={`p-4 md:w-1/3 sm:mb-0 mb-6 transition-opacity ease-in duration-2000 delay-900 ${image2Visible ? "opacity-100" : "opacity-0"}`}
            >
              <div className="rounded-3xl h-64 overflow-hidden border-2 border-blue-950 shadow-2xl">
                <Image
                  alt="content"
                  className="object-cover object-center w-full h-full  shadow-2xl"
                  src={"/lesson2_mainpage.png"}
                  width={1203}
                  height={503}
                />
              </div>
            </div>
            <div
              ref={image3Ref}
              className={`p-4 md:w-1/3 sm:mb-0 mb-6 transition-opacity ease-in duration-2000 delay-1200 ${image3Visible ? "opacity-100" : "opacity-0"}`}
            >
              <div className="rounded-3xl h-64 border-2 border-blue-950 overflow-hidden shadow-2xl">
                <Image
                  alt="content"
                  className="object-cover object-center h-full w-full  shadow-2xl"
                  src={"/lesson3_mainpage.png"}
                  width={1200}
                  height={503}
                />
              </div>
            </div>
          </div>
          <div
            ref={buttonRef}
            className={`flex justify-center mt-8 py-10 transition-opacity ease-in duration-700 delay-1500 ${buttonVisible ? "opacity-100" : "opacity-0"}`}
          >
            <button className="inline-flex text-white bg-blue-950 border-0 py-5 px-12 focus:outline-none rounded-full text-lg shadow-xl">
              
              <Link href="./lessons">
                Go to Lessons
              </Link>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LessonsInfo;
