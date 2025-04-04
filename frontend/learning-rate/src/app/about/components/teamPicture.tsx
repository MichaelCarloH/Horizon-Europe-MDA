import React, { useEffect, useRef, useState } from "react";
import Image from 'next/image';
import FaceRecognition from './facial';

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

const TeamFaceRecognition: React.FC = () => {
  const imageRef = useRef<HTMLDivElement>(null);
  const imageVisible = useIsVisible(imageRef);

  return (
    <div data-testid="team-face-recognition" className="relative flex justify-center items-center h-screen mb-12">
  <div className="relative" ref={imageRef}>
    <Image 
      src="/teamPicture.jpg" 
      alt="Team Picture" 
      width={1000} 
      height={1000}
      className={`rounded-xl border-4 border-black mt-10 transition-opacity ease-in duration-600 ${imageVisible ? "opacity-100" : "opacity-0"}`}
    />
    
    {/* Adjust the positions and sizes below according to the faces in your image */}
    <div className="absolute" style={{ top: '40%', left: '25%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"George-Adelin Aniței"}
            about={"A true Dacian warrior vampire. CEO of Ursus. CEO of Dacia. I drive Dacia Logan, color cantaloupe (bostan-pumpkin). Taxi driver as a hobby. Ultras of STEAUA Bucharest. FCSB is STEAUA. Gluten intolerant and diabetic. Manele listener. Ciorbă >>> Supă crem. Developed pbinfo website."}
            email={"adelin.anitei@yahoo.com"}
            instagram={"@adelin.anitei"}
            width={210} height={280}
            top={140} left={370} imageRef={imageRef}      />
    </div> 

    <div className="absolute" style={{ top: '23%', left: '45%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Michael Carlo"}
            about={"CEO of Ferrari. CEO of Bugatti. Developed Barilla website. "}
            email={"jane.smith@example.com"}
            instagram={"@michaelcarlo_"}
            width={60} height={85}
            top={90} left={500} imageRef={imageRef}      />
    </div>

    <div className="absolute" style={{ top: '29%', left: '54%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Giulio Vitolo"}
            about={"CEO of Fiat. CEO of Peroni Beer. Developed Lamborghini website."}
            email={"vitologiulio@libero.it"}
            instagram={"@giuliovitolo_"}
            width={50} height={65}
            top={130} left={580} imageRef={imageRef}        />
    </div> 

    <div className="absolute" style={{ top: '31%', left: '62%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Yusuf Hussein"}
            about={"Sheikh of Egypt. A beginner software developer from Egypt, not the best at programming, but can build pyramids very quickly. CEO of Microsoft. CEO of Facebook. CEO of Intel. CEO of Ferrari. CEO of European Parliament. CEO of Google. CEO of Ku Leuven. Rector of GroepT."}
            email={" yusuf.hussein@student.kuleuven.be"}
            instagram={"@yusufhosny"}
            width={50} height={60}
            top={180} left={200} imageRef={imageRef}      />
    </div> 

    <div className="absolute" style={{ top: '41%', left: '59%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Random Pedestrian"}
            about={"Seriously, why would you walk right in the middle of our picture!? Like, not cool, bro, not cool. Next time watch where you walk."}
            email={"john.doe@gmail.com"}
            instagram={"@john_doe"}
            width={50} height={60}
            top={220} left={170} imageRef={imageRef}      />
    </div> 

    <div className="absolute" style={{ top: '30%', left: '70.5%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Jaskaran Singh Sidhu"}
            about={"I'm Jaskaran, an Electronics student at KU Leuven. I'm a technology enthusiast and I started working on learning rate because of my interest in machine learning/AI and how to make it more accessible to everybody."}
            email={"jaskaransingh.sidhu@student.kuleuven.be"}
            instagram={"@john_doe"}
            width={50} height={70}
            top={60} left={280} imageRef={imageRef}      />
    </div> 

    <div className="absolute" style={{ top: '34.5%', left: '77.3%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Adham Almeadawy"}
            about={"Grand Vizir of Egypt. Builder of the Sphinx. CEO of camels. CEO of Aramco. Shik Shak Shok. Composer of بشرة خير. Developed UFC website "}
            email={"john.doe@example.com"}
            instagram={"@ad.not.ham"}
            width={52} height={60}
            top={80} left={350} imageRef={imageRef}     />
    </div> 

    <div className="absolute" style={{ top: '48%', left: '83.5%', transform: 'translate(-50%, -50%)' }}>
      <FaceRecognition
            fullName={"Bosu' Boșilor, Gigi Becali"}
            about={"Patron peste toată Pipera. Al doilea om după 'Marele Alb' în biserica ortodoxă română. Președintele țării și al FCSB-ului, distrugătorul domnului Șucu, respectiv Rapidului. Fost europarlamentar și deținut, autor a 2 bibliografii. Lumea îmi mai zice și Moș Crăciun la câți bani dau  de sărbători colindătorilor."}
            email={"john.cena@gmail.com"}
            instagram={"@johncena"}
            width={100} height={124}
            top={200} left={390} imageRef={imageRef}      />
    </div> 
  </div>
</div>

  );
};

export default TeamFaceRecognition;