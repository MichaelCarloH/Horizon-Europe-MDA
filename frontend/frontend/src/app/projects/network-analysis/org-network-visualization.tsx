'use client'

import { useEffect, useState, useRef } from 'react';
import Papa from 'papaparse';
import ForceGraph2D from 'react-force-graph-2d';

interface CollaborationLink {
  organisation1_name: string;
  organisation2_name: string;
  num_of_projects: number;
}

interface OrgCommunity {
  organization_name: string;
  communityId: number;
  country: string;
}

interface Node {
  id: string;
  name: string;
  val: number;
  country?: string;
  isSelected?: boolean;
  isNeighbor?: boolean;
  numSharedProjects?: number; // Added to track shared projects
}

interface Link {
  source: string;
  target: string;
  value: number; // Strength based on num_of_projects
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export default function OrgNetworkVisualization() {
  const [allOrgs, setAllOrgs] = useState<string[]>([]);
  const [selectedOrgs, setSelectedOrgs] = useState<string[]>([]);
  const [isOrgDropdownOpen, setIsOrgDropdownOpen] = useState(false);
  const [orgSearchTerm, setOrgSearchTerm] = useState('');
  const [graphData, setGraphData] = useState<{ nodes: Node[]; links: Link[] }>({ nodes: [], links: [] });
  const [fullLinks, setFullLinks] = useState<Link[]>([]);
  const [fullNodes, setFullNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const orgDropdownRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);

  // Load all orgs and all links/nodes on mount
  useEffect(() => {
    async function fetchData() {
      try {
        const colabResponse = await fetch('/data/org_colab.csv');
        if (!colabResponse.ok) throw new Error('Failed to fetch collaboration data');
        const colabCsvText = await colabResponse.text();
        Papa.parse(colabCsvText, {
          header: true,
          dynamicTyping: true,
          complete: (colabResults) => {
            const colabData = colabResults.data as CollaborationLink[];
            const nodesMap = new Map<string, Node>();
            const links: Link[] = [];
            colabData.forEach(colab => {
              const org1 = String(colab.organisation1_name);
              const org2 = String(colab.organisation2_name);
              const numProjects = colab.num_of_projects as number;
              if (!nodesMap.has(org1)) nodesMap.set(org1, { id: org1, name: org1, val: 1 });
              else nodesMap.get(org1)!.val += 1;
              if (!nodesMap.has(org2)) nodesMap.set(org2, { id: org2, name: org2, val: 1 });
              else nodesMap.get(org2)!.val += 1;
              links.push({ source: org1, target: org2, value: numProjects });
            });
            setAllOrgs(Array.from(nodesMap.keys()).sort());
            setFullNodes(Array.from(nodesMap.values()));
            setFullLinks(links);
            setLoading(false);
          },
          error: (error: any) => { setError('Error parsing CSV: ' + error.message); setLoading(false); }
        });
      } catch (err) { setError('Error loading data: ' + (err instanceof Error ? err.message : String(err))); setLoading(false); }
    }
    fetchData();
  }, []);

  // Build subgraph when selection changes
  useEffect(() => {
    if (selectedOrgs.length === 0) {
      setGraphData({ nodes: [], links: [] });
      return;
    }
    // For each selected org, get its top 25 collaborators by num_of_projects
    const selectedSet = new Set(selectedOrgs);
    let nodeSet = new Set<string>(selectedOrgs);
    let links: Link[] = [];
    // First, collect all relevant links
    selectedOrgs.forEach(org => {
      // Find all links where org is source or target
      const orgLinks = fullLinks.filter(l => l.source === org || l.target === org);
      // Sort by num_of_projects descending
      const sorted = orgLinks.sort((a, b) => b.value - a.value);
      // Take top 25
      const topLinks = sorted.slice(0, 25);
      links = links.concat(topLinks);
      // Add collaborators to node set
      topLinks.forEach(l => {
        nodeSet.add(l.source as string);
        nodeSet.add(l.target as string);
      });
    });
    // Remove duplicate links
    const linkKey = (l: Link) => {
      const s = typeof l.source === 'object' ? (l.source as any).id : l.source;
      const t = typeof l.target === 'object' ? (l.target as any).id : l.target;
      return `${s}--${t}`;
    };
    const uniqueLinksMap = new Map<string, Link>();
    links.forEach(l => {
      uniqueLinksMap.set(linkKey(l), l);
    });
    const uniqueLinks = Array.from(uniqueLinksMap.values());
    // Calculate shared projects for each node
    const sharedProjectsMap = new Map<string, number>();
    // For each node, calculate total number of shared projects with selected organizations
    nodeSet.forEach(nodeId => {
      if (selectedSet.has(nodeId)) {
        // Selected orgs get a higher base value
        sharedProjectsMap.set(nodeId, 10);
      } else {
        let sharedProjects = 0;
        uniqueLinks.forEach(link => {
          const source = typeof link.source === 'object' ? (link.source as any).id : link.source;
          const target = typeof link.target === 'object' ? (link.target as any).id : link.target;
          // If this link connects current node with any selected org, add its value
          if ((source === nodeId && selectedSet.has(target)) || 
              (target === nodeId && selectedSet.has(source))) {
            sharedProjects += link.value;
          }
        });
        sharedProjectsMap.set(nodeId, sharedProjects);
      }
    });
    // Preserve node positions if possible
    const prevNodeMap = new Map<string, any>();
    graphData.nodes.forEach(n => {
      prevNodeMap.set(n.id, n);
    });
    // Build nodes array with shared projects information
    const nodes = Array.from(nodeSet).map(id => {
      const base = fullNodes.find(n => n.id === id)!;
      const numSharedProjects = sharedProjectsMap.get(id) || 1;
      const prev = prevNodeMap.get(id);
      // Only preserve fx/fy if they are not null/undefined (i.e., user fixed them by dragging)
      const preserveFixed = prev && (prev.fx !== undefined && prev.fx !== null && prev.fy !== undefined && prev.fy !== null);
      return {
        ...base,
        id,
        name: base.name || id,
        isSelected: selectedOrgs.includes(id),
        isNeighbor: !selectedOrgs.includes(id),
        numSharedProjects: numSharedProjects,
        val: selectedOrgs.includes(id) 
          ? Math.max(5, Math.min(25, Math.sqrt(numSharedProjects) * 2.5)) 
          : Math.max(3, Math.min(20, Math.sqrt(numSharedProjects) * 2)),
        // Always preserve position and velocity
        ...(prev && {
          x: prev.x,
          y: prev.y,
          vx: prev.vx,
          vy: prev.vy
        }),
        // Only preserve fx/fy if they are not null/undefined
        ...(preserveFixed && {
          fx: prev.fx,
          fy: prev.fy
        })
      };
    });
    setGraphData({ nodes, links: uniqueLinks });
  }, [selectedOrgs, fullLinks, fullNodes]);

  // Apply enhanced force simulation when graph data changes
  useEffect(() => {
    if (graphRef.current && graphData.nodes.length > 0) {
      try {
        // We're going to adjust the view only once - NOT on every data change
        // Only zoom to fit if this is the first time loading for this selection
        if (!graphRef.current.__dataInitialized) {
          setTimeout(() => {
            if (graphRef.current) {
              try {
                // Zoom to fit nodes only on initial load
                graphRef.current.zoomToFit(400);
                // Mark that we've initialized view for this data
                graphRef.current.__dataInitialized = true;
              } catch (e) {
                console.error("Error centering graph:", e);
              }
            }
          }, 1000); // Give more time for layout to settle
        }
      } catch (e) {
        console.error("Error configuring graph:", e);
      }
    }
    
    // Reset initialization flag when graph data changes
    return () => {
      if (graphRef.current) {
        graphRef.current.__dataInitialized = false;
      }
    };
  }, [graphData]);

  // Dropdown/filter logic (unchanged)
  const toggleOrgSelection = (org: string) => {
    setSelectedOrgs(prev => prev.includes(org) ? prev.filter(o => o !== org) : [...prev, org]);
  };
  const handleOrgSearch = (e: React.ChangeEvent<HTMLInputElement>) => setOrgSearchTerm(e.target.value);
  const filteredOrgs = allOrgs.filter(org => org.toLowerCase().includes(orgSearchTerm.toLowerCase()));
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (orgDropdownRef.current && !orgDropdownRef.current.contains(event.target as Element)) {
        setIsOrgDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => { document.removeEventListener('mousedown', handleClickOutside); };
  }, []);

  // Node color: red for selected, blue for neighbor
  const getNodeColor = (node: any) => node.isSelected ? '#e3342f' : node.isNeighbor ? '#2563eb' : '#aaa';
  
  // Node label: first letter of org name, with size based on numSharedProjects
  const getNodeCanvasObject = (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    // Calculate node radius based on val (which is set according to numSharedProjects)
    const nodeSize = node.val || 5;
    const radius = Math.sqrt(nodeSize) * 1.8;
    
    const label = node.name ? node.name[0] : '?';
    ctx.font = `${Math.max(10, Math.min(20, nodeSize * 0.8))/globalScale}px Sans-Serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = getNodeColor(node);
    ctx.fill();
    
    // Add border for better visibility
    ctx.strokeStyle = node.isSelected ? '#c81e1e' : '#fff';
    ctx.lineWidth = 0.5;
    ctx.stroke();
    
    // Draw text label
    ctx.fillStyle = '#fff';
    ctx.fillText(label, node.x, node.y);
    
    // Show node tooltip on hover (optional)
    if (node.__hovered) {
      const fontSize = 12/globalScale;
      ctx.font = `${fontSize}px Sans-Serif`;
      const textWidth = ctx.measureText(node.name).width;
      const backgroundHeight = fontSize + 4;
      const backgroundWidth = textWidth + 6;
      
      // Draw background for tooltip
      ctx.fillStyle = 'rgba(0,0,0,0.8)';
      ctx.fillRect(node.x - backgroundWidth/2, node.y - radius - backgroundHeight - 2, backgroundWidth, backgroundHeight);
      
      // Draw tooltip text
      ctx.fillStyle = 'white';
      ctx.fillText(node.name, node.x, node.y - radius - 4);
    }
  };

  if (loading) return <div className="flex justify-center p-10"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div></div>;
  if (error) return <div className="text-red-500 p-4 border border-red-300 rounded">{error}</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-xl font-medium mb-4">Organization Collaboration Network</h3>
      <div className="mb-4 relative w-full md:w-64" ref={orgDropdownRef}>
        <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Organizations</label>
        <div className="relative">
          <button type="button" className="flex justify-between items-center px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 w-full" onClick={() => setIsOrgDropdownOpen(!isOrgDropdownOpen)}>
            <span className="truncate">{selectedOrgs.length === 0 ? 'Select organizations' : `${selectedOrgs.length} organization${selectedOrgs.length > 1 ? 's' : ''} selected`}</span>
            <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
          </button>
          {isOrgDropdownOpen && (
            <div className="absolute z-10 w-full mt-1 bg-white shadow-lg rounded-md border border-gray-300 max-h-60 overflow-y-auto">
              <div className="p-2 border-b sticky top-0 bg-white">
                <input type="text" placeholder="Search organizations..." className="w-full px-3 py-1.5 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" value={orgSearchTerm} onChange={handleOrgSearch} />
              </div>
              <div className="p-1">
                {filteredOrgs.length > 0 ? (
                  filteredOrgs.map((org) => (
                    <div key={org} className="flex items-center px-2 py-1.5 hover:bg-gray-100 cursor-pointer" onClick={() => toggleOrgSelection(org)}>
                      <input type="checkbox" checked={selectedOrgs.includes(org)} onChange={() => {}} className="h-4 w-4 mr-2 text-blue-600 focus:ring-blue-500" />
                      <label className="text-sm cursor-pointer truncate" title={org}>{org}</label>
                    </div>
                  ))
                ) : (
                  <div className="px-3 py-2 text-sm text-gray-500">No organizations found</div>
                )}
              </div>
              <div className="flex justify-between items-center p-2 border-t bg-gray-50">
                <button className="text-xs text-blue-600 hover:text-blue-800" onClick={e => { e.stopPropagation(); setSelectedOrgs([]); }}>Clear all</button>
                <span className="text-xs text-gray-500">{selectedOrgs.length} selected</span>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Only show graph if at least one org is selected */}
      {graphData.nodes.length > 0 && (
        <div className="relative w-full h-[600px] border border-gray-200 rounded-lg">
          <div className="absolute top-2 right-2 z-10">
            <button 
              className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              onClick={() => {
                if (graphRef.current) {
                  graphRef.current.zoomToFit(400, 30);
                }
              }}
            >
              Center Graph
            </button>
          </div>
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel={node => `${node.name} (${node.numSharedProjects || 0} shared projects)`}
            nodeColor={getNodeColor}
            nodeRelSize={6}
            linkWidth={link => Math.sqrt((link as any).value) * 0.5}
            linkColor={() => 'rgba(187, 187, 187, 0.6)'}
            nodeCanvasObject={getNodeCanvasObject}
            cooldownTicks={100}
            d3AlphaDecay={0.01}
            d3VelocityDecay={0.7}
            enableNodeDrag={true}
            enableZoomInteraction={true}
            minZoom={0.4}
            maxZoom={5}
            warmupTicks={50}
            onNodeDrag={node => {
              // Allow free movement, do not clamp or fix node
              node.fx = node.x;
              node.fy = node.y;
            }}
            onNodeDragEnd={node => {
              // Release node so simulation can move it again
              node.fx = null;
              node.fy = null;
            }}
            width={document.querySelector(".w-full.h-\\[600px\\]")?.clientWidth}
            height={document.querySelector(".w-full.h-\\[600px\\]")?.clientHeight}
          />
        </div>
      )}
      {selectedOrgs.length === 0 && (
        <div className="mt-4 text-sm text-gray-500">Select one or more organizations to view their collaboration network.</div>
      )}
      {selectedOrgs.length > 0 && graphData.nodes.length === 0 && (
        <div className="mt-4 text-sm text-gray-500">No collaborations found for the selected organization(s).</div>
      )}
      {graphData.nodes.length > 0 && (
        <div className="mt-4 text-sm text-gray-600">
          <p className="font-medium">Network visualization guide:</p>
          <ul className="list-disc pl-5 mt-1">
            <li><span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-1"></span> Selected organizations</li>
            <li><span className="inline-block w-3 h-3 bg-blue-600 rounded-full mr-1"></span> Collaborating organizations</li>
            <li>Node size indicates number of shared projects</li>
            <li>Hover over nodes to see organization names</li>
          </ul>
        </div>
      )}
    </div>
  );
}
