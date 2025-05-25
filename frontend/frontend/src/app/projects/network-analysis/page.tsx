'use client'

import CentralityAnalysis from "./centrality-analysis.tsx";
import OrgNetworkVisualization from "./org-network-visualization.tsx";

export default function NetworkAnalysisPage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Network Analysis Dashboard (2024 Projects)</h1>
      
      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Centrality Analysis</h2>
        <p className="mb-6 text-gray-700">
          This dashboard visualizes the centrality measures of organizations in the Horizon Europe network.
          Centrality metrics help identify the most influential and well-connected organizations in the research collaboration network.
        </p>
        <CentralityAnalysis />
      </section>
      
      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-4">Organization Collaboration Network</h2>
        <p className="mb-6 text-gray-700">
          This visualization shows the collaborative relationships between organizations. By default, the top 25 collaborative relationships are displayed. Use the filter to focus on specific organizations.
        </p>
        <OrgNetworkVisualization />
      </section>
    </main>
  );
}
