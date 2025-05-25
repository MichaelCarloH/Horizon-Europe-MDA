'use client'

import CentralityAnalysis from "./centrality-analysis";

export default function NetworkAnalysisPage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Network Analysis Dashboard</h1>
      
      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Centrality Analysis</h2>
        <p className="mb-6 text-gray-700">
          This dashboard visualizes the centrality measures of organizations in the Horizon Europe network.
          Centrality metrics help identify the most influential and well-connected organizations in the research collaboration network.
        </p>
        <CentralityAnalysis />
      </section>
    </main>
  );
}
