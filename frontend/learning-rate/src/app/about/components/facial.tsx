import React, { useState, useRef } from 'react';
import Popup from './Popup';
import { createPortal } from 'react-dom';

interface PersonalInfoProps {
  fullName: string;
  about: string;
  email: string;
  instagram: string;
  width: number;
  height: number;
  top: number;  // Add top position prop
  left: number; // Add left position prop
  imageRef: React.RefObject<HTMLDivElement>;
}

const FaceRecognition: React.FC<PersonalInfoProps> = ({ fullName, about, email, instagram, width, height, top, left, imageRef }) => {
  const [isOpen, setIsOpen] = useState(false);
  const popupContainerRef = useRef<HTMLDivElement>(null);

  const handleClick = () => {
    setIsOpen(!isOpen);
  };

  const cornerRadius = Math.min(width, height) * 0.4; // Example for 40% corner radius
  const path = `
    M${cornerRadius},0 
    h${width - 2 * cornerRadius} 
    a${cornerRadius},${cornerRadius} 0 0 1 ${cornerRadius},${cornerRadius} 
    v${height - 2 * cornerRadius} 
    a${cornerRadius},${cornerRadius} 0 0 1 -${cornerRadius},${cornerRadius} 
    h-${width - 2 * cornerRadius} 
    a${cornerRadius},${cornerRadius} 0 0 1 -${cornerRadius},-${cornerRadius} 
    v-${height - 2 * cornerRadius} 
    a${cornerRadius},${cornerRadius} 0 0 1 ${cornerRadius},-${cornerRadius} 
    z`;

  return (
    <div
      className="relative cursor-pointer"
      ref={popupContainerRef}
      onClick={handleClick}
    >
      <div>
        <svg
          width={width}
          height={height}
          className="cursor-pointer" 
          data-testid="face-recognition-svg"
        >
          <path
            d={path}
            fill="none"
            stroke="yellow"
            strokeWidth="3"
          />
        </svg>
      </div>
      {isOpen && createPortal(
        <Popup
          onClose={() => setIsOpen(false)}
          fullName={fullName}
          about={about}
          email={email}
          instagram={instagram}
          style={{ top: top, left: left, position: 'absolute' }}
        />, 
        imageRef.current!
      )}
    </div>
  );
};

export default FaceRecognition;
