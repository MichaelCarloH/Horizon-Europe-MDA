"use client";

import React, { useState } from 'react';
import Popup from '../signup-signin/popup';
import { signIn } from "next-auth/react"


const LoginButton: React.FC<{}> = () => {
  const [isPopupOpen, setIsPopupOpen] = useState<boolean>(false);

  
  return (
    <div>
      <button className="flex text-center text-xl bg-blue-950 border-0 py-2 px-6 focus:outline-none rounded-lg shadow-xl m-2" onClick={() => setIsPopupOpen(true)}>
            Sign In
          </button>

      {isPopupOpen && <Popup onClose={() => setIsPopupOpen(false)} startState='login' />}
    </div>
  );
};

export default LoginButton;
