import React, { useRef } from 'react';
import PersonalInfo from './personalInfo';

interface PopupProps {
  onClose: () => void;
  fullName: string;
  about: string;
  email: string;
  instagram: string;
  style: React.CSSProperties;
}

const Popup: React.FC<PopupProps> = ({ onClose, fullName, about, email, instagram, style }) => {
  const popupRef = useRef(null);

  const popupStyle: React.CSSProperties = {
    ...style,
    zIndex: 9999, // Ensure the popup is on top of other elements
  };

  return (
    <div 
      className='absolute bg-white p-8 rounded-lg shadow-lg max-w-lg w-96'
      ref={popupRef}
      style={popupStyle} 
    >
      <div className='flex justify-between align-center mb-2'>
        <button className="text-3xl cursor-pointer bg-none text-black hover:text-gray-500" onClick={onClose}>&times;</button>
      </div>
      <PersonalInfo 
        fullName={fullName}
        about={about}
        email={email}
        instagram={instagram}
      />
    </div>
  );
};

export default Popup;
