import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegistrationForm from '../app/components/signup-signin/registration_form/form_registration';
import { skillLevelContext } from '@/app/components/signup-signin/registration_form/skill_ctx';

describe('RegistrationForm Component', () => {
  const mockOnRegisterSuccess = jest.fn();

  const fillStep1 = () => {
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'Doe' } });
    fireEvent.click(screen.getByText(/Next/i));
  };

  const fillStep2 = () => {
    fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'johndoe' } });
    fireEvent.change(screen.getByLabelText(/skill Level/i), { target: { value: 0 } });
    fireEvent.click(screen.getByText(/Next/i));
  };

  const fillStep3 = () => {
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'john.doe@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByText(/Register/i));
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn(() => Promise.reject(new Error('Registration failed')));
    console.error = jest.fn();
  });

  test('should render the form and fill step 1 correctly', () => {
    render(
      <skillLevelContext.Provider value={ {levels: [
        {
          skillLevelID: 0,
          skillname: 'Beginner',
        },
        {
          skillLevelID: 1,
          skillname: 'Hobbyist',
        },
        {
          skillLevelID: 2,
          skillname: 'Intermediate',
        },
        {
          skillLevelID: 3,
          skillname: 'Expert',
        },
      ]} }>
        <RegistrationForm onRegisterSuccess={mockOnRegisterSuccess} />
      </skillLevelContext.Provider>
  );

    // Check if the form is rendered
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();

    // Fill step 1
    fillStep1();

    // Check if the next step is rendered
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
  });

  test('should render the form and fill step 2 correctly', () => {
    render(
      <skillLevelContext.Provider value={ {levels: [
        {
          skillLevelID: 0,
          skillname: 'Beginner',
        },
        {
          skillLevelID: 1,
          skillname: 'Hobbyist',
        },
        {
          skillLevelID: 2,
          skillname: 'Intermediate',
        },
        {
          skillLevelID: 3,
          skillname: 'Expert',
        },
      ]} }>
        <RegistrationForm onRegisterSuccess={mockOnRegisterSuccess} />
      </skillLevelContext.Provider>
  );

    // Check if the form is rendered
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();

    // Fill step 1 and 2
    fillStep1();
    fillStep2();

    // Check if the next step is rendered
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
  });

  test('should render the form and fill step 3 correctly', async () => {
    render(
      <skillLevelContext.Provider value={ {levels: [
        {
          skillLevelID: 0,
          skillname: 'Beginner',
        },
        {
          skillLevelID: 1,
          skillname: 'Hobbyist',
        },
        {
          skillLevelID: 2,
          skillname: 'Intermediate',
        },
        {
          skillLevelID: 3,
          skillname: 'Expert',
        },
      ]} }>
        <RegistrationForm onRegisterSuccess={mockOnRegisterSuccess} />
      </skillLevelContext.Provider>
  );

    // Check if the form is rendered
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();

    // Fill step 1 and 2 and 3
    fillStep1();
    fillStep2();
    fillStep3();

  });


  test('should handle error during registration process', async () => {
    // Mock the fetch function to reject the Promise with an error
    global.fetch = jest.fn(() => Promise.reject(new Error('Registration failed')));
  
    // Render the RegistrationForm component
    render(
      <skillLevelContext.Provider value={ {levels: [
        {
          skillLevelID: 0,
          skillname: 'Beginner',
        },
        {
          skillLevelID: 1,
          skillname: 'Hobbyist',
        },
        {
          skillLevelID: 2,
          skillname: 'Intermediate',
        },
        {
          skillLevelID: 3,
          skillname: 'Expert',
        },
      ]} }>
        <RegistrationForm onRegisterSuccess={mockOnRegisterSuccess} />
      </skillLevelContext.Provider>
  );
  
    // Fill steps 1, 2, and 3
    fillStep1();
    fillStep2();
    fillStep3();
  
    // Wait for form submission
    await waitFor(() => {
      // Check if the error is logged
      expect(console.error).toHaveBeenCalledWith('An error occurred:', expect.any(Error));
  
      // Ensure that the onRegisterSuccess callback is not called
      expect(mockOnRegisterSuccess).not.toHaveBeenCalled();
    });
  });
  
  test('should handle previous step correctly', () => {
    render(
      <skillLevelContext.Provider value={ {levels: [
        {
          skillLevelID: 0,
          skillname: 'Beginner',
        },
        {
          skillLevelID: 1,
          skillname: 'Hobbyist',
        },
        {
          skillLevelID: 2,
          skillname: 'Intermediate',
        },
        {
          skillLevelID: 3,
          skillname: 'Expert',
        },
      ]} }>
        <RegistrationForm onRegisterSuccess={mockOnRegisterSuccess} />
      </skillLevelContext.Provider>
  );

    // Check if the form is rendered with step 1
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/Email/i)).not.toBeInTheDocument(); // Step 3 should not be visible

    // Fill step 1
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'Doe' } });
    fireEvent.click(screen.getByText(/Next/i));

    // Check if step 2 is rendered
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();

    // Click the "Previous" button
    fireEvent.click(screen.getByText(/Previous/i));

    // Check if step 1 is rendered again
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/Username/i)).not.toBeInTheDocument(); // Step 2 should not be visible
  });
});

