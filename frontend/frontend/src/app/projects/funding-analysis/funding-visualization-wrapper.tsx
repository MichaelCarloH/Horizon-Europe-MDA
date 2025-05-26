'use client'

import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import FundingVisualization from './funding-visualization';

export default function FundingVisualizationWrapper() {
  return (
    <Suspense fallback={
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
      </div>
    }>
      <FundingVisualization />
    </Suspense>
  );
}
