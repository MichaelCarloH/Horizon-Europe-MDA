"use client";

import React, { useState } from 'react';
import Popup from '../signup-signin/popup'; 
import { skillLevelContext } from "../signup-signin/registration_form/skill_ctx";

const RegisterButton: React.FC<{levels: {skillLevelID: number, skillname: string}[]}> = ({levels}) => {
  const [isPopupOpen, setIsPopupOpen] = useState<boolean>(false);

  
  return (
    <div>
      <button 
        className="flex text-center text-xl bg-blue-950 border-0 py-2 px-6 focus:outline-none rounded-lg shadow-xl"
        onClick={() => setIsPopupOpen(true)}
      >
        Register
      </button>
      <skillLevelContext.Provider value={ {levels: levels} }>
        {isPopupOpen && <Popup onClose={() => setIsPopupOpen(false)} startState='register' />}
      </skillLevelContext.Provider>
    </div>
  );
};

export default RegisterButton;
