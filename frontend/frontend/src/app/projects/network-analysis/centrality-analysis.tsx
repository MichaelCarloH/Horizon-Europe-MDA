'use client'

import { useEffect, useState, useRef } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Papa from 'papaparse';

interface OrgCentrality {
  organization_name: string;
  pagerank_score: number;
  degree_centrality_score: number;
  betweenness_score: number;
  country?: string;
}

export default function CentralityAnalysis() {
  const [centralityData, setCentralityData] = useState<OrgCentrality[]>([]);
  const [filteredData, setFilteredData] = useState<OrgCentrality[]>([]);
  const [selectedOrgs, setSelectedOrgs] = useState<string[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<keyof OrgCentrality>('pagerank_score');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uniqueOrgs, setUniqueOrgs] = useState<string[]>([]);
  const [uniqueCountries, setUniqueCountries] = useState<string[]>([]);
  const [isOrgDropdownOpen, setIsOrgDropdownOpen] = useState(false);
  const [isCountryDropdownOpen, setIsCountryDropdownOpen] = useState(false);
  const [orgSearchTerm, setOrgSearchTerm] = useState('');
  const [countrySearchTerm, setCountrySearchTerm] = useState('');
  
  // Refs for handling clicks outside the dropdowns
  const orgDropdownRef = useRef<HTMLDivElement>(null);
  const countryDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchCentralityData() {
      try {
        const response = await fetch('/data/centrality_analysis.csv');
        if (!response.ok) {
          throw new Error('Failed to fetch centrality data');
        }
        
        const csvText = await response.text();
        
        // Parse CSV
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: true,
          complete: (results) => {
            // Convert string values to numbers for scores
            const data = results.data as OrgCentrality[];
            
            // Sort by pagerank score descending by default
            const sortedData = [...data].sort((a, b) => 
              (b[sortBy] as number) - (a[sortBy] as number)
            );
            
            // Extract unique organizations and countries for dropdown filters
            const orgs = new Set<string>();
            const countries = new Set<string>();
            
            data.forEach(item => {
              if (item.organization_name) {
                orgs.add(typeof item.organization_name === 'string' ? 
                  item.organization_name : String(item.organization_name));
              }
              if (item.country) {
                countries.add(typeof item.country === 'string' ? 
                  item.country : String(item.country));
              }
            });
            
            setUniqueOrgs(Array.from(orgs).sort());
            setUniqueCountries(Array.from(countries).sort());
            setCentralityData(sortedData);
            setFilteredData(sortedData);
            setLoading(false);
          },
          error: (error: any) => {
            setError('Error parsing CSV: ' + error.message);
            setLoading(false);
          }
        });
      } catch (err) {
        setError('Error loading data: ' + (err instanceof Error ? err.message : String(err)));
        setLoading(false);
      }
    }

    fetchCentralityData();
  }, [sortBy]);

  // Apply filters when selections change
  useEffect(() => {
    let filtered = [...centralityData];
    
    // Filter by selected organizations
    if (selectedOrgs.length > 0) {
      filtered = filtered.filter(org => 
        selectedOrgs.includes(String(org.organization_name))
      );
    }
    
    // Filter by selected countries
    if (selectedCountries.length > 0) {
      filtered = filtered.filter(org => 
        org.country && selectedCountries.includes(String(org.country))
      );
    }
    
    // Apply sorting
    filtered = filtered.sort((a, b) =>
      (b[sortBy] as number) - (a[sortBy] as number)
    );
    
    setFilteredData(filtered);
  }, [centralityData, selectedOrgs, selectedCountries, sortBy]);
  
  // Handle clicks outside of dropdown menus
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (orgDropdownRef.current && !orgDropdownRef.current.contains(event.target as Node)) {
        setIsOrgDropdownOpen(false);
      }
      if (countryDropdownRef.current && !countryDropdownRef.current.contains(event.target as Node)) {
        setIsCountryDropdownOpen(false);
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Helper functions for organization selection
  const toggleOrgSelection = (org: string) => {
    setSelectedOrgs(prev => 
      prev.includes(org) 
        ? prev.filter(o => o !== org) 
        : [...prev, org]
    );
  };
  
  const handleOrgSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOrgSearchTerm(e.target.value);
  };
  
  const filteredOrgs = uniqueOrgs.filter(org => 
    org.toLowerCase().includes(orgSearchTerm.toLowerCase())
  );
  
  // Helper functions for country selection  
  const toggleCountrySelection = (country: string) => {
    setSelectedCountries(prev => 
      prev.includes(country) 
        ? prev.filter(c => c !== country) 
        : [...prev, country]
    );
  };
  
  const handleCountrySearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCountrySearchTerm(e.target.value);
  };
  
  const filteredCountries = uniqueCountries.filter(country => 
    country.toLowerCase().includes(countrySearchTerm.toLowerCase())
  );

  const top15PageRank = [...centralityData]
    .sort((a, b) => b.pagerank_score - a.pagerank_score)
    .slice(0, 15);
  const top15Degree = [...centralityData]
    .sort((a, b) => b.degree_centrality_score - a.degree_centrality_score)
    .slice(0, 15);
  const top15Betweenness = [...centralityData]
    .sort((a, b) => b.betweenness_score - a.betweenness_score)
    .slice(0, 15);

  if (loading) return <div className="flex justify-center p-10"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div></div>;
  if (error) return <div className="text-red-500 p-4 border border-red-300 rounded">{error}</div>;

  return (
    <div>
      {/* Bar Charts Section - Each in its own row for better readability */}
      <div className="flex flex-col gap-10 mb-10">
        {/* PageRank Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-medium mb-4">Top 15 Organizations by PageRank</h3>
          <div className="h-[500px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top15PageRank}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 250, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis 
                  type="category" 
                  dataKey="organization_name" 
                  tick={{ fontSize: 12 }}
                  width={250}
                />
                <Tooltip 
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(5) : value)}
                  labelFormatter={(label) => `Organization: ${label}`}
                  wrapperStyle={{ 
                    maxWidth: '600px', 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                    padding: '10px', 
                    border: '1px solid #ccc',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    overflow: 'hidden',
                    wordBreak: 'break-word'
                  }}
                />
                <Legend />
                <Bar dataKey="pagerank_score" fill="#8884d8" name="PageRank" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Degree Centrality Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-medium mb-4">Top 15 Organizations by Degree Centrality</h3>
          <div className="h-[500px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top15Degree}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 250, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis 
                  type="category" 
                  dataKey="organization_name" 
                  tick={{ fontSize: 12 }}
                  width={250}
                />
                <Tooltip 
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(2) : value)}
                  labelFormatter={(label) => `Organization: ${label}`}
                  wrapperStyle={{ 
                    maxWidth: '600px', 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                    padding: '10px', 
                    border: '1px solid #ccc',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    overflow: 'hidden',
                    wordBreak: 'break-word'
                  }}
                />
                <Legend />
                <Bar dataKey="degree_centrality_score" fill="#82ca9d" name="Degree Centrality" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Betweenness Centrality Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-medium mb-4">Top 15 Organizations by Betweenness</h3>
          <div className="h-[500px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top15Betweenness}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 250, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis 
                  type="category" 
                  dataKey="organization_name" 
                  tick={{ fontSize: 12 }}
                  width={250}
                />
                <Tooltip 
                  formatter={(value: any) => (typeof value === 'number' ? value.toFixed(0) : value)}
                  labelFormatter={(label) => `Organization: ${label}`}
                  wrapperStyle={{ 
                    maxWidth: '600px', 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                    padding: '10px', 
                    border: '1px solid #ccc',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    overflow: 'hidden',
                    wordBreak: 'break-word'
                  }}
                />
                <Legend />
                <Bar dataKey="betweenness_score" fill="#ffc658" name="Betweenness" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Search and Table Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex flex-col md:flex-row items-start justify-between mb-6 gap-4">
          <h3 className="text-xl font-semibold">Organization Centrality Data</h3>
          <div className="flex flex-col w-full md:w-auto gap-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Organization Filter */}
              <div className="relative w-full md:w-64" ref={orgDropdownRef}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Organization
                </label>
                <div className="relative">
                  <button
                    type="button"
                    className="flex justify-between items-center px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
                    onClick={() => setIsOrgDropdownOpen(!isOrgDropdownOpen)}
                  >
                    <span className="truncate">
                      {selectedOrgs.length === 0 
                        ? 'Select organizations' 
                        : `${selectedOrgs.length} organization${selectedOrgs.length > 1 ? 's' : ''} selected`}
                    </span>
                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {isOrgDropdownOpen && (
                    <div className="absolute z-10 w-full mt-1 bg-white shadow-lg rounded-md border border-gray-300 max-h-60 overflow-y-auto">
                      <div className="p-2 border-b sticky top-0 bg-white">
                        <input
                          type="text"
                          placeholder="Search organizations..."
                          className="w-full px-3 py-1.5 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          value={orgSearchTerm}
                          onChange={handleOrgSearch}
                        />
                      </div>
                      <div className="p-1">
                        {filteredOrgs.length > 0 ? (
                          filteredOrgs.map((org) => (
                            <div 
                              key={org} 
                              className="flex items-center px-2 py-1.5 hover:bg-gray-100 cursor-pointer"
                              onClick={() => toggleOrgSelection(org)}
                            >
                              <input
                                type="checkbox"
                                checked={selectedOrgs.includes(org)}
                                onChange={() => {}}
                                className="h-4 w-4 mr-2 text-blue-600 focus:ring-blue-500"
                              />
                              <label className="text-sm cursor-pointer truncate" title={org}>
                                {org}
                              </label>
                            </div>
                          ))
                        ) : (
                          <div className="px-3 py-2 text-sm text-gray-500">No organizations found</div>
                        )}
                      </div>
                      <div className="flex justify-between items-center p-2 border-t bg-gray-50">
                        <button 
                          className="text-xs text-blue-600 hover:text-blue-800"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedOrgs([]);
                          }}
                        >
                          Clear all
                        </button>
                        <span className="text-xs text-gray-500">{selectedOrgs.length} selected</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Country Filter */}
              <div className="relative w-full md:w-64" ref={countryDropdownRef}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Country
                </label>
                <div className="relative">
                  <button
                    type="button"
                    className="flex justify-between items-center px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
                    onClick={() => setIsCountryDropdownOpen(!isCountryDropdownOpen)}
                  >
                    <span className="truncate">
                      {selectedCountries.length === 0 
                        ? 'Select countries' 
                        : `${selectedCountries.length} ${selectedCountries.length > 1 ? 'countries' : 'country'} selected`}
                    </span>
                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {isCountryDropdownOpen && (
                    <div className="absolute z-10 w-full mt-1 bg-white shadow-lg rounded-md border border-gray-300 max-h-60 overflow-y-auto">
                      <div className="p-2 border-b sticky top-0 bg-white">
                        <input
                          type="text"
                          placeholder="Search countries..."
                          className="w-full px-3 py-1.5 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          value={countrySearchTerm}
                          onChange={handleCountrySearch}
                        />
                      </div>
                      <div className="p-1">
                        {filteredCountries.length > 0 ? (
                          filteredCountries.map((country) => (
                            <div 
                              key={country} 
                              className="flex items-center px-2 py-1.5 hover:bg-gray-100 cursor-pointer"
                              onClick={() => toggleCountrySelection(country)}
                            >
                              <input
                                type="checkbox"
                                checked={selectedCountries.includes(country)}
                                onChange={() => {}}
                                className="h-4 w-4 mr-2 text-blue-600 focus:ring-blue-500"
                              />
                              <label className="text-sm cursor-pointer">{country}</label>
                            </div>
                          ))
                        ) : (
                          <div className="px-3 py-2 text-sm text-gray-500">No countries found</div>
                        )}
                      </div>
                      <div className="flex justify-between items-center p-2 border-t bg-gray-50">
                        <button 
                          className="text-xs text-blue-600 hover:text-blue-800"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedCountries([]);
                          }}
                        >
                          Clear all
                        </button>
                        <span className="text-xs text-gray-500">{selectedCountries.length} selected</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Sort Option */}
            <div className="w-full md:w-64">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort Results By
              </label>
              <select 
                className="px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
                value={sortBy}
                onChange={e => setSortBy(e.target.value as keyof OrgCentrality)}
              >
                <option value="pagerank_score">PageRank Score</option>
                <option value="degree_centrality_score">Degree Centrality</option>
                <option value="betweenness_score">Betweenness Score</option>
              </select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Organization
                </th>
                {centralityData[0]?.country && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
                  </th>
                )}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PageRank Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Degree Centrality
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Betweenness Score
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredData.slice(0, 20).map((org, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {org.organization_name}
                  </td>
                  {org.country && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {org.country}
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {typeof org.pagerank_score === 'number' ? org.pagerank_score.toFixed(5) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {typeof org.degree_centrality_score === 'number' ? org.degree_centrality_score.toFixed(2) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {typeof org.betweenness_score === 'number' ? Math.round(org.betweenness_score).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredData.length === 0 && (
            <div className="text-center py-4 text-gray-500">No results found matching your filter criteria</div>
          )}
          {filteredData.length > 20 && (
            <div className="text-center py-4 text-gray-500">
              Showing 20 of {filteredData.length} results. {(selectedOrgs.length > 0 || selectedCountries.length > 0) ? 
                'You can modify your selection of organizations and countries to refine results.' : 
                'Select one or more organizations or countries to filter results.'}
            </div>
          )}
          {filteredData.length > 0 && filteredData.length <= 20 && (
            <div className="text-center py-4 text-gray-500">
              Showing all {filteredData.length} results
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
