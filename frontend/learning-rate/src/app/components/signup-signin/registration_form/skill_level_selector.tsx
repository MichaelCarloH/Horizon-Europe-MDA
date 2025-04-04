import React, { useContext } from 'react';
import { skillLevelContext } from './skill_ctx';

interface skillLevelProps {
  skillLevel: number,
  handleChange: (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
};

const SkillLevelSelector = ({ skillLevel, handleChange}: skillLevelProps) => {
  
    const { levels } = useContext(skillLevelContext);

    return (
    <div className="flex flex-col mb-4" >
      
        <label htmlFor="skillLevel" className="text-gray-700 mb-2">skill Level:</label>
        <select
          id="skillLevel"
          name="skillLevel"
          value={skillLevel}
          onChange={handleChange}
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        >
          { levels.map( (level, i) => (<option
                key={i}
                value={level.skillLevelID}
            > {level.skillname} </option>) ) }
        </select>

    </div>
  );
};

export default SkillLevelSelector;
