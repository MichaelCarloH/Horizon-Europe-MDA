import React, { useRef } from 'react';

interface PopupProps {
  onClose: () => void;
  content: string; // Text to show in popup
  title?: string;   // Optional title (e.g. organization name)
}

const Popup: React.FC<PopupProps> = ({ onClose, content, title }) => {
  const popupRef = useRef(null);

  return (
    <div className='fixed top-0 left-0 w-full h-full bg-black/50 flex items-center justify-center z-50'>
      <div className='bg-white p-6 rounded-lg shadow-lg max-w-md animate-fadein w-[28rem]' ref={popupRef}>
        <div className='flex justify-between items-center mb-4'>
          <h2 className='text-xl font-bold text-gray-900'>{title || 'Details'}</h2>
          <button className="text-3xl cursor-pointer text-black hover:text-gray-500" onClick={onClose}>&times;</button>
        </div>

        <div className="text-gray-800 whitespace-pre-line">
          {content}
        </div>
      </div>
    </div>
  );
};

export default Popup;
