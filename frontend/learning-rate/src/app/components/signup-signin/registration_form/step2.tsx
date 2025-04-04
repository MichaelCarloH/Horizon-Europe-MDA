import React from 'react';
import SkillLevelSelector from './skill_level_selector';

interface RegistrationData {
  skillLevel: number;
  username: string;
}

interface Step2Props {
  skillLevel: number;
  username: string;
  onChange: (updatedData: Partial<RegistrationData>) => void;
  onNext: () => void;
  onPrev: () => void;
}

const Step2: React.FC<Step2Props> = ({ skillLevel, username, onChange, onNext, onPrev }) => {

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    
    const updatedValue = name === 'skillLevel' ? parseInt(value, 10) : value;

    onChange({ [name]: updatedValue }); 
  };

  return (
    <div>

      <SkillLevelSelector skillLevel={skillLevel} handleChange={handleChange}/>

      <div className="flex flex-col mb-4">
        <label htmlFor="username" className="text-gray-700 mb-2">Username:</label>
        <input
          type="text"
          id="username"
          name="username"
          value={username}
          onChange={handleChange}
          required
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div>

      <div className="flex gap-2 mt-6">
        <button type="button" onClick={onPrev} className="bg-gray-500 text-white py-2 px-4 rounded focus:outline-none">
          Previous
        </button>
        <button type="button" onClick={onNext} className="bg-blue-500 text-white py-2 px-4 rounded focus:outline-none">
          Next
        </button>
      </div>
    </div>
  );
};

export default Step2;
