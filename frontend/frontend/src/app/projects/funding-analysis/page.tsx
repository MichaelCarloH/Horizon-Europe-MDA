'use client'

import { useState } from "react";
import FundingVisualizationWrapper from "./funding-visualization-wrapper";

export default function FundingAnalysisPage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Research Topic Funding Analysis</h1>
      
      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Quarterly Funding by Research Topic</h2>
        <p className="mb-6 text-gray-700">
          This visualization shows the quarterly funding amounts distributed across different research topics.
          Use the filter to select specific research topics and compare their funding trends over time.
        </p>
        <FundingVisualizationWrapper />
      </section>
    </main>
  );
}
