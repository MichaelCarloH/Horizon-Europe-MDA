import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SkillLevelSelector from '../app/components/signup-signin/registration_form/skill_level_selector'; // Adjust the import path as needed

describe('SkillLevelSelector Component', () => {
  const initialProps = {
    skillLevel: 2,
    handleChange: jest.fn(),
  };

  test('should render correctly with initial props', () => {
    render(<SkillLevelSelector {...initialProps} />);

    const selectElement = screen.getByLabelText(/skill Level/i);

    expect(selectElement).toBeInTheDocument();
  });

});
