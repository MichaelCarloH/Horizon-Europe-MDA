'use client'

import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

// Interface definitions for our data
interface FundingData {
  project_id: string;
  title: string;
  euroscivoc_final: string;
  ecMaxContribution: number;
  startDate: string;
  endDate: string;
  totalCost: number;
}

interface QuarterlyData {
  quarter: string;
  [key: string]: number | string; // Dynamic keys for each topic
}

interface QuarterlyProjectCount {
  quarter: string;
  [key: string]: number | string; // Dynamic keys for each topic (project count)
}

interface TopicCount {
  topic: string;
  totalFunding: number;
  projectCount: number;
}

// Function to parse a date string and return a quarter string (e.g., "2022-Q1")
const getQuarter = (dateString: string): string => {
  if (!dateString) return "Unknown";
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = date.getMonth();
  const quarter = Math.floor(month / 3) + 1;
  return `${year}-Q${quarter}`;
};

export default function FundingVisualization() {
  const [rawData, setRawData] = useState<FundingData[]>([]);
  const [quarterlyData, setQuarterlyData] = useState<QuarterlyData[]>([]);
  const [quarterlyProjectCounts, setQuarterlyProjectCounts] = useState<QuarterlyProjectCount[]>([]);
  const [availableTopics, setAvailableTopics] = useState<TopicCount[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
  const [topicSearchTerm, setTopicSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      const dropdown = document.getElementById('topic-dropdown');
      if (isDropdownOpen && dropdown && !dropdown.contains(target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  // Load and process data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/data/topic_with_funding.csv');
        if (!response.ok) throw new Error('Failed to fetch data');
        
        const csvText = await response.text();
        
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: true,
          complete: (results) => {
            const data = results.data as FundingData[];
            
            // Filter out rows with missing essential data
            const validData = data.filter(row => 
              row.project_id && 
              row.euroscivoc_final && 
              row.ecMaxContribution && 
              row.startDate
            );
            
            setRawData(validData);
            processData(validData);
            setLoading(false);
          },
          error: (error: any) => {
            setError(`Error parsing CSV: ${error.message}`);
            setLoading(false);
          }
        });
      } catch (error) {
        setError(`Error fetching data: ${error instanceof Error ? error.message : String(error)}`);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Process raw data into quarterly funding by topic
  const processData = (data: FundingData[]) => {
    // Calculate total funding per topic and count projects per topic
    const topicFundingMap: Map<string, number> = new Map();
    const topicProjectCountMap: Map<string, number> = new Map();
    
    data.forEach(project => {
      const topic = project.euroscivoc_final;
      const funding = Number(project.ecMaxContribution);
      
      if (topic) {
        // Count projects per topic
        if (topicProjectCountMap.has(topic)) {
          topicProjectCountMap.set(topic, topicProjectCountMap.get(topic)! + 1);
        } else {
          topicProjectCountMap.set(topic, 1);
        }
        
        // Sum funding per topic
        if (!isNaN(funding)) {
          if (topicFundingMap.has(topic)) {
            topicFundingMap.set(topic, topicFundingMap.get(topic)! + funding);
          } else {
            topicFundingMap.set(topic, funding);
          }
        }
      }
    });

    // Create sorted list of topics by project count (primary) and funding (secondary)
    const topicsByCount: TopicCount[] = Array.from(topicProjectCountMap.entries())
      .map(([topic, count]) => ({ 
        topic, 
        totalFunding: topicFundingMap.get(topic) || 0,
        projectCount: count 
      }))
      .sort((a, b) => b.projectCount - a.projectCount || b.totalFunding - a.totalFunding);
    
    setAvailableTopics(topicsByCount);
    
    // Default to top 10 topics by project count
    const top10Topics = topicsByCount.slice(0, 10).map((item: TopicCount) => item.topic);
    setSelectedTopics(top10Topics);

    // Group projects by quarter and topic for funding
    const quarterFundingMap: Map<string, Map<string, number>> = new Map();
    // Group projects by quarter and topic for project counts
    const quarterProjectCountMap: Map<string, Map<string, number>> = new Map();
    
    // Track unique projects by quarter and topic to avoid duplicates
    const projectTracker: Map<string, Set<string>> = new Map();
    
    data.forEach(project => {
      if (!project.startDate || !project.euroscivoc_final) return;
      
      const quarter = getQuarter(project.startDate);
      const topic = project.euroscivoc_final;
      const projectId = project.project_id;
      const funding = Number(project.ecMaxContribution);
      
      // Initialize nested maps for funding if needed
      if (!quarterFundingMap.has(quarter)) {
        quarterFundingMap.set(quarter, new Map());
      }
      
      // Initialize nested maps for project counts if needed
      if (!quarterProjectCountMap.has(quarter)) {
        quarterProjectCountMap.set(quarter, new Map());
      }
      
      // Initialize project tracker if needed
      if (!projectTracker.has(quarter)) {
        projectTracker.set(quarter, new Set());
      }
      
      // Track project to avoid double counting
      const quarterProjects = projectTracker.get(quarter)!;
      const isNewProjectForQuarter = !quarterProjects.has(projectId);
      if (isNewProjectForQuarter) {
        quarterProjects.add(projectId);
      }
      
      // Update funding
      if (!isNaN(funding)) {
        const topicFundingMap = quarterFundingMap.get(quarter)!;
        if (topicFundingMap.has(topic)) {
          topicFundingMap.set(topic, topicFundingMap.get(topic)! + funding);
        } else {
          topicFundingMap.set(topic, funding);
        }
      }
      
      // Update project counts
      const topicProjectCountMap = quarterProjectCountMap.get(quarter)!;
      if (topicProjectCountMap.has(topic)) {
        topicProjectCountMap.set(topic, topicProjectCountMap.get(topic)! + 1);
      } else {
        topicProjectCountMap.set(topic, 1);
      }
    });
    
    // Convert the nested maps to the format recharts expects
    const sortedQuarters = Array.from(quarterFundingMap.keys()).sort();
    
    // Process funding data
    const fundingChartData: QuarterlyData[] = sortedQuarters.map(quarter => {
      const quarterData: QuarterlyData = { quarter };
      const topicMap = quarterFundingMap.get(quarter)!;
      
      topicMap.forEach((funding, topic) => {
        quarterData[topic] = Math.round(funding / 1000); // Convert to thousands for readability
      });
      
      return quarterData;
    });
    
    // Process project count data
    const projectCountChartData: QuarterlyProjectCount[] = sortedQuarters.map(quarter => {
      const quarterData: QuarterlyProjectCount = { quarter };
      const topicMap = quarterProjectCountMap.get(quarter)!;
      
      topicMap.forEach((count, topic) => {
        quarterData[topic] = count;
      });
      
      return quarterData;
    });
    
    setQuarterlyData(fundingChartData);
    setQuarterlyProjectCounts(projectCountChartData);
  };

  // Toggle topic selection
  const toggleTopic = (topic: string) => {
    setSelectedTopics(prev => 
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  // Select all topics
  const selectAllTopics = () => {
    setSelectedTopics(availableTopics.map(item => item.topic));
  };

  // Clear all selected topics
  const clearTopics = () => {
    setSelectedTopics([]);
  };

  // Select top N topics
  const selectTopNTopics = (n: number) => {
    const topN = availableTopics.slice(0, n).map(item => item.topic);
    setSelectedTopics(topN);
  };

  // Generate a unique color for each topic (based on its index)
  const getTopicColor = (topic: string, index: number) => {
    const colors = [
      '#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe', 
      '#00c49f', '#ffbb28', '#ff8042', '#a4de6c', '#d0ed57'
    ];
    
    const topicIndex = availableTopics.findIndex(t => t.topic === topic);
    return colors[topicIndex % colors.length];
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
    </div>
  );

  if (error) return (
    <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
      <p>{error}</p>
    </div>
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Filter by Research Topic</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          <button 
            onClick={() => selectTopNTopics(10)}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
          >
            Top 10
          </button>
          <button 
            onClick={() => selectTopNTopics(20)}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
          >
            Top 20
          </button>
          <button 
            onClick={selectAllTopics}
            className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
          >
            Select All
          </button>
          <button 
            onClick={clearTopics}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
          >
            Clear All
          </button>
        </div>
        
        <div className="relative">
          <div 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="border rounded p-3 flex justify-between items-center cursor-pointer bg-white"
          >
            <div className="truncate">
              {selectedTopics.length === 0 ? 
                "Select research topics" : 
                `${selectedTopics.length} topic${selectedTopics.length > 1 ? 's' : ''} selected`}
            </div>
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
          
          {isDropdownOpen && (
            <div id="topic-dropdown" className="absolute z-10 mt-1 w-full bg-white border rounded-md shadow-lg max-h-60 overflow-y-auto">
              <div className="sticky top-0 bg-white border-b p-2">
                <input 
                  type="text" 
                  placeholder="Search topics..." 
                  className="w-full border rounded p-2 text-sm"
                  value={topicSearchTerm}
                  onChange={(e) => setTopicSearchTerm(e.target.value)}
                />
              </div>
              <div className="p-2">
                {availableTopics
                  .filter(item => item.topic.toLowerCase().includes(topicSearchTerm.toLowerCase()))
                  .map((item, index) => (
                  <div key={item.topic} className="flex items-center py-1 hover:bg-gray-100 px-2 rounded">
                    <input
                      type="checkbox"
                      id={`topic-${index}`}
                      checked={selectedTopics.includes(item.topic)}
                      onChange={() => toggleTopic(item.topic)}
                      className="mr-2 h-4 w-4"
                    />
                    <label htmlFor={`topic-${index}`} className="text-sm cursor-pointer flex-grow">
                      <span className="font-medium">{item.topic}</span>
                      <div className="text-xs text-gray-500">
                        {item.projectCount} project{item.projectCount !== 1 ? 's' : ''} · 
                        {(item.totalFunding / 1000000).toFixed(1)}M €
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="h-[500px] mt-6">
        <h3 className="text-lg font-medium mb-2">Quarterly Funding by Research Topic (in thousands €)</h3>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart
            data={quarterlyData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="quarter" />
            <YAxis />
            <Tooltip 
              formatter={(value, name, props) => [`${value}k €`, name]} 
              labelFormatter={(label) => `Quarter: ${label}`}
            />
            <Legend />
            {selectedTopics.map((topic, index) => (
              <Line
                key={topic}
                type="monotone"
                dataKey={topic}
                name={topic}
                stroke={getTopicColor(topic, index)}
                activeDot={{ r: 8 }}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="h-[500px] mt-10 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-medium mb-2">Quarterly Number of Projects by Research Topic</h3>
        <ResponsiveContainer width="100%" height="90%">
          <LineChart
            data={quarterlyProjectCounts}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="quarter" />
            <YAxis />
            <Tooltip 
              formatter={(value, name, props) => [`${value} projects`, name]} 
              labelFormatter={(label) => `Quarter: ${label}`}
            />
            <Legend />
            {selectedTopics.map((topic, index) => (
              <Line
                key={topic}
                type="monotone"
                dataKey={topic}
                name={topic}
                stroke={getTopicColor(topic, index)}
                activeDot={{ r: 8 }}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
