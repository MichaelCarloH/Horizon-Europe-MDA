import React from 'react';

interface PersonalInfoProps {
  fullName: string;
  about: string;
  email: string;
  instagram: string;
}

const PersonalInfo: React.FC<PersonalInfoProps> = ({ fullName, about, email, instagram }) => {
  return (
    <div className='bg-white p-4 rounded-lg shadow-lg w-80'>
      <h2 className='text-2xl font-bold text-gray-900'>{fullName}</h2>
      <p className='text-gray-700 mt-2'>{about}</p>
      <div className='mt-4'>
        <p className='text-gray-700'><strong>Email:</strong> <a href={`mailto:${email}`} className='text-blue-500 hover:underline' target="_blank" rel="noopener noreferrer">{email}</a></p>
        <p className='text-gray-700'><strong>Instagram:</strong> <a href={`https://instagram.com/${instagram}`} className='text-blue-500 hover:underline' target="_blank" rel="noopener noreferrer">{instagram}</a></p>
      </div>
    </div>
  );
};

export default PersonalInfo;
