import React from 'react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep, totalSteps }) => {
  const progressPercentage = Math.round((currentStep / totalSteps) * 100);

  return (
    <div className="relative w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
      <div
        className="bg-blue-600 h-2.5 rounded-full"
        style={{ width: `${progressPercentage}%` }}
      >
        <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs text-white">
          {currentStep}/{totalSteps}
        </span>
      </div>
    </div>
  );
};

export default ProgressBar;
