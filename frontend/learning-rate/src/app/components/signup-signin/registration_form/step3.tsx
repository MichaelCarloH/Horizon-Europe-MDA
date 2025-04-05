import React from 'react';

interface RegistrationData { // Define the interface here
  email: string;
  password: string;
  // ... other fields (age, university, email, password)
}
interface Step3Props {
  email: string;
  password: string;
  onChange: (updatedData: Partial<RegistrationData>) => void;
  onPrev: () => void;
}

const Step3: React.FC<Step3Props> = ({ email, password, onChange, onPrev }) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    onChange({ [name]: value }); 
  };

  
  return (
    <div>
      <div className="flex flex-col mb-4">
        <label htmlFor="email" className="text-gray-700 mb-2">Email:</label>
        <input
          type="email"
          id="email"
          name="email" 
          value={email}
          onChange={handleChange}
          required
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div>

      <div className="flex flex-col mb-4">
        <label htmlFor="password" className="text-gray-700 mb-2">Password:</label>
        <input
          type="password"
          id="password"
          name="password"
          value={password}
          onChange={handleChange}
          required
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div> 
      
    </div>
  );
};

export default Step3;
