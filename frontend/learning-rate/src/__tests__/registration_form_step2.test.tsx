import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Step2 from '../app/components/signup-signin/registration_form/step2';

describe('Step2 Component', () => {
  const initialProps = {
    skillLevel: 0,
    username: '',
    onChange: jest.fn(),
    onNext: jest.fn(),
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
    render(<Step2 {...initialProps} />);

    const skillLevelInput = screen.getByLabelText('skill Level:');
    fireEvent.change(skillLevelInput, { target: { value: 0 } });

    expect(onChange).toHaveBeenCalled();
  });

  test('should call onChange with correct data when username input changes', () => {
    const { onChange } = initialProps;
    render(<Step2 {...initialProps} />);

    const username = screen.getByLabelText('Username:');
    fireEvent.change(username, { target: { value: 'demonSlayer44' } });

    expect(onChange).toHaveBeenCalledWith({ username: 'demonSlayer44' });
  });

  test('should call onNext when the next button is clicked', () => {
    const { onNext } = initialProps;
    render(<Step2 {...initialProps} />);

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    expect(onNext).toHaveBeenCalled();
  });

  test('should call onPrev when the prev button is clicked', () => {
    const { onPrev } = initialProps;
    render(<Step2 {...initialProps} />);

    const prevButton = screen.getByText('Previous');
    fireEvent.click(prevButton);

    expect(onPrev).toHaveBeenCalled();
  });
});
