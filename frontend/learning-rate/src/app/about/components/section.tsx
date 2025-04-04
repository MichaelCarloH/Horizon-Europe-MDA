import React, { useEffect, useRef, useState } from "react";
import Image from 'next/image';

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

interface IconProps {
  title: string;
  paragraph: string;
  image: string;
  leftToRight: boolean;
  imgW: number;
  imgH:number;
  alternative: string
}

const Section: React.FC<IconProps> = ({ title, paragraph, image, leftToRight, imgW, imgH, alternative }) => {
  const headerRef = useRef<HTMLDivElement>(null);
  const paragraphRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  const headerVisible = useIsVisible(headerRef);
  const paragraphVisible = useIsVisible(paragraphRef);
  const imageVisible = useIsVisible(imageRef);

  return (
    <div className="grid grid-cols-2 gap-4 place-items-center mb-40 mt-10"> 
      {leftToRight ? (
        <>
          <div data-testid="left-container" className="w-1/2">
            <div
              ref={headerRef}
              className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
            >
              <h2 className="text-4xl font-bold mb-4">{title}</h2>
            </div>
            <div
              ref={paragraphRef}
              className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
            >
              <p className="mb-4 text-lg">{paragraph}</p>
            </div>
          </div>
          <div
            ref={imageRef}
            className={`transition-opacity ease-in duration-2000 delay-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
          >
            <Image 
              src={image} 
              alt={alternative}
              width={imgW}
              height={imgH}
              className="rounded-lg mt-5 mb-5"
            />
          </div>
        </>
      ) : (
        <>
          <div
            ref={imageRef}
            className={`transition-opacity ease-in duration-2000 delay-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
          >
            <Image 
              src={image} 
              alt="An icon of a lightbulb to represent learning and ideas."
              width={500}
              height={500}
              className="rounded-lg mt-5 mb-5"
            />
          </div>
          <div data-testid="right-container" className="w-1/2">
            <div
              ref={headerRef}
              className={`transition-opacity ease-in duration-700 ${headerVisible ? "opacity-100" : "opacity-0"}`}
            >
              <h2 className="text-4xl font-bold mb-4">{title}</h2>
            </div>
            <div
              ref={paragraphRef}
              className={`transition-opacity ease-in duration-700 delay-300 ${paragraphVisible ? "opacity-100" : "opacity-0"}`}
            >
              <p className="mb-4 text-lg">{paragraph}</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Section;
