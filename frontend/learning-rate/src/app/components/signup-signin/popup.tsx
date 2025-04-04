import React, { useRef, useState } from 'react';
import RegistrationForm from './registration_form/form_registration'; 
import Image from 'next/image';
import LoginForm from './login_form/login_form';

interface PopupProps {
  onClose: () => void;
  startState: string
}

const Popup: React.FC<PopupProps> = ({ onClose, startState }) => {
  const [activeState, setActiveState] = useState(startState); 
  const popupRef = useRef(null);


  const handleSwitchState = (nextState: 'register' | 'login' | 'success') => {
    setActiveState(nextState);
  };

  return (
    <div className='fixed top-0 left-0 w-full h-full bg-black/50 flex items-center justify-center z-50'>
      <div className='bg-white p-8 rounded-lg shadow-lg max-w-lg animate-fadein w-96 h-96' ref={popupRef}>
        <div className='flex justify-between align-center mb-2'>
            <h2 className='text-2xl font-bold text-gray-900'>
              {activeState === 'register' && 'Register'}
              {activeState === 'login' && 'Log in'}
              {activeState === 'success' && 'Success'}
            </h2>
          <button className="text-3xl cursor-pointer bg-none text-black hover:text-gray-500" onClick={onClose}>&times;</button>
        </div>

        {activeState === 'register' && (
          <>
            <RegistrationForm onRegisterSuccess={() => handleSwitchState('success')}/>
            <button className='text-sky-700 hover:underline' onClick={() => setActiveState('login')}> 
              Already have an account? <strong>Login now</strong>
            </button>
          </>
        )}

        {activeState === 'login' && (
          <>
            <LoginForm/>
            <button className='text-sky-700 hover:underline' onClick={() => setActiveState('register')}> 
              Don&apos;t have an account? <strong>Make one</strong>
            </button>
          </>
        )}

        {activeState === 'success' && (
          <div>
            Registration successful!  <button className='text-sky-700 hover:underline' onClick={() => setActiveState('login')}>You can now log in</button>
            <Image
            src={"/check_icon.jpg"}
            alt="Neuron"
            width={80}
            height={80}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Popup;
