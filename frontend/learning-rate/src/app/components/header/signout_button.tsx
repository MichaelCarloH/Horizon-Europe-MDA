"use client";

import React from 'react';
import { signOut } from 'next-auth/react';


const SignOutButton: React.FC<{}> = () => {
  
  return (
    <div>

    <button 
        className="flex text-center text-xl bg-blue-950 border-0 py-2 px-6 focus:outline-none rounded-lg shadow-xl m-2" 
        onClick={() => signOut()}>
        Sign Out
    </button>

    </div>
  );
};

export default SignOutButton;
