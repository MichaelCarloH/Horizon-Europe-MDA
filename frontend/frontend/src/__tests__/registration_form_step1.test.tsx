import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Step1 from '../app/components/signup-signin/registration_form/step1';

describe('Step1 Component', () => {
  const initialProps = {
    name: 'John',
    lastName: 'Doe',
    onChange: jest.fn(),
    onNext: jest.fn(),
  };
  
  test('should call onChange with correct data when name input changes', () => {
    const { onChange } = initialProps;
    render(<Step1 {...initialProps} />);

    const nameInput = screen.getByLabelText('First Name:');
    fireEvent.change(nameInput, { target: { value: 'Jane' } });

    expect(onChange).toHaveBeenCalledWith({ name: 'Jane' });
  });

  test('should call onChange with correct data when last name input changes', () => {
    const { onChange } = initialProps;
    render(<Step1 {...initialProps} />);

    const lastNameInput = screen.getByLabelText('Last Name:');
    fireEvent.change(lastNameInput, { target: { value: 'Smith' } });

    expect(onChange).toHaveBeenCalledWith({ lastName: 'Smith' });
  });

  test('should call onNext when the next button is clicked', () => {
    const { onNext } = initialProps;
    render(<Step1 {...initialProps} />);

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    expect(onNext).toHaveBeenCalled();
  });
});
