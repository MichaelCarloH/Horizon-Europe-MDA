// src/__tests__/step1.test.ts
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
//import '@testing-library/jest-dom/extend-expect';
import Step3 from '../app/components/signup-signin/registration_form/step3';

describe('Step3 Component', () => {
  const initialProps = {
    email: "",
    password: 'demonslayer44',
    onChange: jest.fn(),
    onPrev: jest.fn(),
  };
  /*
  test('should render correctly with initial props', () => {
    render(<Step1 {...initialProps} />);

    expect(screen.getByLabelText('Name:')).toHaveValue('John');
    expect(screen.getByLabelText('Last Name:')).toHaveValue('Doe');
  });
  */
  test('should call onChange with correct data when skillLevel input changes', () => {
    const { onChange } = initialProps;
    render(<Step3 {...initialProps} />);

    const emaillInput = screen.getByLabelText('Email:');
    fireEvent.change(emaillInput, { target: { value: 'urloAtomicoDelSiuuum@RealMadrid.be'  } });

    expect(onChange).toHaveBeenCalledWith({ email: 'urloAtomicoDelSiuuum@RealMadrid.be'});
  });

  test('should call onChange with correct data when username input changes', () => {
    const { onChange } = initialProps;
    render(<Step3 {...initialProps} />);

    const passwordInput = screen.getByLabelText('Password:');
    fireEvent.change(passwordInput, { target: { value: 'demonSlayer44' } });

    expect(onChange).toHaveBeenCalledWith({ password: 'demonSlayer44' });
  });
  /* previous button is in rgeistration for last step
  test('should call onPrev when the prev button is clicked', () => {
    const { onPrev } = initialProps;
    render(<Step3 {...initialProps} />);

    const prevButton = screen.getByText('Previous');
    fireEvent.click(prevButton);

    expect(onPrev).toHaveBeenCalled();
  });*/ 
});
