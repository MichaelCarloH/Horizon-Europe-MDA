import React from 'react';

interface RegistrationData { // Define the interface here
  name: string;
  lastName: string;
  // ... other fields (age, university, email, password)
}

interface Step1Props {
  name: string;         // Only name prop
  lastName: string;      // Only lastName prop
  onChange: (updatedData: Partial<RegistrationData>) => void; 
  onNext: () => void;
}

const Step1: React.FC<Step1Props> = ({ name, lastName, onChange, onNext }) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    onChange({ [name]: value });  // Construct partial update object
  };

  return (
    <div>
      <div className="flex flex-col mb-4">
        <label htmlFor="name" className="text-gray-700 mb-2">First Name:</label>
        <input
          type="text"
          id="name"
          name="name" // Important for partial update
          value={name}  
          onChange={handleChange}
          required
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div>

      <div className="flex flex-col mb-4">
        <label htmlFor="lastName" className="text-gray-700 mb-2">Last Name:</label>
        <input
          type="text"
          id="lastName"
          name="lastName" // Important for partial update
          value={lastName}  
          onChange={handleChange}
          required
          className="border border-gray-300 text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
      </div>

      <button type="button" onClick={onNext} className="bg-blue-500 text-white py-2 px-4 rounded focus:outline-none">
        Next
      </button>
    </div>
  );
};

export default Step1;
