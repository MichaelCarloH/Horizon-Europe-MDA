"use client"

import React from 'react';
import { loginAction } from '@/actions/login';


const LoginForm: React.FC<{}> = () => {

  return (
    <div>
        {
        <form
            action = {loginAction}
        >
            <div className="flex flex-col p-4 w-full">

                <label className="text-gray-700 mb-2">
                    Email:
                </label>
                <input name="email" type="email" className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"/>
                
                <label className="text-gray-700 mb-2">
                    Password:
                </label>
                <input name="password" type="password" className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600" />
                
                <button type="submit" className="bg-blue-500 text-white py-2 px-4 mt-4 rounded focus:outline-none w-fit self-center">
                    Log in
                </button>

            </div>
        </form>
        }
    </div>
  );
};

export default LoginForm;
