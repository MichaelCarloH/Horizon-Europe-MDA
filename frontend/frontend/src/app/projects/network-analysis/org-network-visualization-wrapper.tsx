"use client";

import dynamic from "next/dynamic";

const OrgNetworkVisualization = dynamic(
  () => import("./org-network-visualization"),
  { ssr: false }
);

export default function OrgNetworkVisualizationWrapper() {
  return <OrgNetworkVisualization />;
}
