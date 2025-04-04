"use client"

import React, { useEffect, useState } from 'react';
import ProgressBar from '../progress_bar';
import { hashPassword } from '@/utils/password';
import { z } from 'zod';
import Step1 from './step1';
import Step2 from './step2';
import Step3 from './step3';


// Zod schema for registration data validation
export const registrationSchema = z.object({
  name: z.string().min(1, 'Name is required').min(2, 'Name must be at least 2 characters long'),
  lastName: z.string().min(1, 'Last name is required').min(2, 'Last name must be at least 2 characters long'),
  skillLevel: z.number(),
  username: z.string().min(1, 'Username is required').min(3, 'Username must be at least 3 characters long'),
  email: z.string().email('Invalid email address').min(1, 'Email is required'),
  password: z.string().min(1, 'Password is required').min(6, 'Password must be at least 6 characters long'),
});

// Infer the RegistrationData type from the Zod schema
export type RegistrationData = z.infer<typeof registrationSchema>;

interface FormProps {
  onRegisterSuccess: () => void;
}

const RegistrationForm: React.FC<FormProps> = ({ onRegisterSuccess }) => {
  const [formData, setFormData] = useState<RegistrationData>({
    name: '',
    lastName: '',
    skillLevel: 0,
    username: '',
    email: '',
    password: '',
  });

  const [csrfToken, setCsrfToken] = useState<string>('Loading...');
  
  useEffect(() => {
    const el = document.querySelector('meta[name="x-csrf-token"]') as HTMLMetaElement | null;
    if (el) setCsrfToken(el.content);
    else setCsrfToken('missing');
  }, []);

  // State for form validation errors
  const [errors, setErrors] = useState<Partial<Record<keyof RegistrationData, string>>>({});

  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3; 

  const handleChange = (step: number, updatedData: Partial<RegistrationData>) => {
    setFormData((prevFormData) => ({
      ...prevFormData,
      ...updatedData,
    }));
    setErrors({}); // Clear errors when form data changes
  };

  // Validate the current step based on the corresponding schema
  const validateStep = (step: number) => {
    const schema = getStepSchema(step); 
    const result = schema.safeParse(formData); 

    if (!result.success) {
      // If validation fails, set the errors
      const validationErrors = result.error.format();
      setErrors(validationErrors as Partial<Record<keyof RegistrationData, string>>);
      console.log(validationErrors) // TODO: Display those errors for the user.
      return false;
    }

    setErrors({}); // Clear errors if validation succeeds
    return true;
  };

  //Based on which step we are in, pick the fields to be edited and stuff.
  const getStepSchema = (step: number) => {
    switch (step) {
      case 1:
        return registrationSchema.pick({ name: true, lastName: true });
      case 2:
        return registrationSchema.pick({ username: true, skillLevel: true });
      case 3:
        return registrationSchema.pick({ email: true, password: true });
      default:
        throw new Error('Invalid step number');
    }
  };

  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // Handle form submission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Validate the current step before submitting
    if (!validateStep(currentStep)) {
      return;
    }

    const hashedPassword = hashPassword(formData.password);
    const dataWithHashedPassword = { ...formData, password: await hashedPassword };

    try {
      // Send a POST request to the server with the form data
      const response = await fetch('/api/auth/register', {
        headers: { 'X-CSRF-Token': csrfToken },
        method: 'POST',
        body: JSON.stringify(dataWithHashedPassword),
      });

      if (response.ok) {
        // If registration is successful, call the onRegisterSuccess callback
        onRegisterSuccess();
      } else {
        console.log('Registration Failed.');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        {/* Progress bar component */}
        <ProgressBar currentStep={currentStep} totalSteps={totalSteps} />

        {/* Hidden field for CSRF token */}
        <input type="hidden" name="token_csrf" value={csrfToken} />

        {currentStep === 1 && (
          <Step1
            name={formData.name}
            lastName={formData.lastName}
            onChange={(updatedData) => handleChange(1, updatedData)}
            onNext={handleNextStep}
          />
        )}

        {currentStep === 2 && (
          <Step2
            skillLevel={formData.skillLevel}
            username={formData.username}
            onChange={(updatedData) => handleChange(2, updatedData)}
            onNext={handleNextStep}
            onPrev={handlePrevStep}
          />
        )}

        {currentStep === 3 && (
          <Step3
            email={formData.email}
            password={formData.password}
            onChange={(updatedData) => handleChange(3, updatedData)}
            onPrev={handlePrevStep}
          />
        )}

        {/* Render navigation buttons based on the current step */}
        <div className="flex gap-2 mt-6">
          {currentStep === totalSteps && (
            <button onClick={handlePrevStep} className="bg-gray-500 text-white py-2 px-4 rounded focus:outline-none">
              Previous
            </button>
          )}

          {currentStep === totalSteps && (
            <button type="submit" className="bg-green-500 text-white py-2 px-4 rounded focus:outline-none">
              Register
            </button>
          )}
        </div>
      </div>
    </form>
  );
};

export default RegistrationForm;