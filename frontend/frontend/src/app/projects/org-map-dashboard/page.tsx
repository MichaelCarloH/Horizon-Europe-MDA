'use client'

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Papa from 'papaparse';

// Dynamically import the map component to avoid SSR issues
const MapComponent = dynamic(() => import('./map-component'), {
    ssr: false,
    loading: () => <div className="h-[600px] bg-gray-100 flex items-center justify-center">Loading map...</div>
});

interface Organization {
    organisationID: string;
    organizationName: string;
    country: string;
    numofProjects: number;
    totalecContribution: number;
    latitude: number;
    longitude: number;
    topic: string;
    project_id: string;
}

interface Project {
    id: string;
    startDate: string;
    endDate: string;
    ecMaxContribution: number;
}

interface OrgCSVRow {
    topic: string;
    organisationID: string;
    name: string;
    country: string;
    latitude: string;
    longitude: string;
    project_id: string;
}

interface ProjectCSVRow {
    id: string;
    startDate: string;
    endDate: string;
    ecMaxContribution: string;
}

export default function OrgMapDashboard() {
    const [data, setData] = useState<Organization[]>([]);
    const [projectData, setProjectData] = useState<Map<string, Project>>(new Map());
    const [selectedTopics, setSelectedTopics] = useState<string[]>(["machine learning"]);
    const [allTopics, setAllTopics] = useState<string[]>([]);
    const [topicSearch, setTopicSearch] = useState('');
    const [topN, setTopN] = useState<number>(25);
    const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
    const [allCountries, setAllCountries] = useState<string[]>([]);
    const [countrySearch, setCountrySearch] = useState('');
    const [error, setError] = useState<string | null>(null);

    // Filter topics based on search
    const filteredTopics = allTopics.filter(topic => 
        topic.toLowerCase().includes(topicSearch.toLowerCase())
    );

    // Filter countries based on search
    const filteredCountries = allCountries.filter(country => 
        country.toLowerCase().includes(countrySearch.toLowerCase())
    );

    useEffect(() => {
        // Load both CSV files
        Promise.all([
            fetch('/data/org_by_research2.csv').then(response => response.text()),
            fetch('/data/project_costs2.csv').then(response => response.text())
        ])
        .then(([orgCsv, projectCsv]) => {
            // Parse project costs data first
            Papa.parse<ProjectCSVRow>(projectCsv, {
                header: true,
                skipEmptyLines: true,
                complete: (projectResults) => {
                    try {
                        // Create a map of project IDs to their costs
                        const projectMap = new Map<string, Project>();
                        projectResults.data.forEach(row => {
                            projectMap.set(row.id, {
                                id: row.id,
                                startDate: row.startDate,
                                endDate: row.endDate,
                                ecMaxContribution: Number(row.ecMaxContribution) || 0
                            });
                        });

                        // Now parse organization data
                        Papa.parse<OrgCSVRow>(orgCsv, {
                            header: true,
                            skipEmptyLines: true,
                            complete: (orgResults) => {
                                try {
                                    const parsedData = orgResults.data
                                        .filter(row => row.latitude && row.longitude)
                                        .map(row => ({
                                            organisationID: String(row.organisationID || ''),
                                            organizationName: String(row.name || ''),
                                            country: String(row.country || ''),
                                            project_id: String(row.project_id || ''),
                                            latitude: Number(row.latitude) || 0,
                                            longitude: Number(row.longitude) || 0,
                                            topic: String(row.topic || ''),
                                            // These will be calculated later
                                            numofProjects: 0,
                                            totalecContribution: 0
                                        }));

                                    // Get unique topics and countries
                                    const topics = Array.from(new Set(parsedData.map(org => org.topic))).filter(Boolean);
                                    const countries = Array.from(new Set(parsedData.map(org => org.country))).filter(Boolean).sort();
                                    
                                    setAllTopics(topics);
                                    setAllCountries(countries);
                                    
                                    // Ensure "machine learning" is in the list and selected
                                    if (topics.includes("machine learning")) {
                                        setSelectedTopics(["machine learning"]);
                                    }
                                    
                                    // Process for display (aggregate by org and topic)
                                    // We'll calculate project counts and contributions in the filtering step
                                    setData(parsedData);
                                    setProjectData(projectMap);
                                    setError(null);
                                } catch (err: any) {
                                    setError('Error parsing organization data: ' + err.message);
                                    console.error('Error parsing organization data:', err);
                                }
                            },
                            error: (err: Error) => {
                                setError('Error loading organization data: ' + err.message);
                                console.error('Error loading organization data:', err);
                            }
                        });
                    } catch (err: any) {
                        setError('Error parsing project data: ' + err.message);
                        console.error('Error parsing project data:', err);
                    }
                },
                error: (err: Error) => {
                    setError('Error loading project data: ' + err.message);
                    console.error('Error loading project data:', err);
                }
            });
        })
        .catch(err => {
            setError('Error fetching data: ' + err.message);
            console.error('Error fetching data:', err);
        });
    }, []);

    // Filter data based on selected topics, countries and top N
    // Also calculate project counts and contributions
    const filteredData = React.useMemo(() => {
        if (selectedTopics.length === 0 && selectedCountries.length === 0) {
            return [];
        }

        // First, get all project IDs that match ALL of the selected topics
        let projectsThatMatchAllTopics = new Set<string>();
        
        // If no topics selected, include all projects
        if (selectedTopics.length === 0) {
            data.forEach(org => {
                projectsThatMatchAllTopics.add(org.project_id);
            });
        } else {
            // Start with projects that match the first topic
            const projectsByTopic = new Map<string, Set<string>>();
            
            // Group projects by topic
            selectedTopics.forEach(topic => {
                projectsByTopic.set(topic, new Set<string>());
            });
            
            // Fill the sets with projects that match each topic
            data.forEach(org => {
                if (selectedTopics.includes(org.topic)) {
                    projectsByTopic.get(org.topic)?.add(org.project_id);
                }
            });
            
            // Find the intersection of all topic project sets
            if (selectedTopics.length === 1) {
                // If only one topic, just use those projects
                projectsThatMatchAllTopics = projectsByTopic.get(selectedTopics[0]) || new Set();
            } else {
                // For each project, check if it exists in all topic sets
                const allProjects = new Set<string>();
                data.forEach(org => allProjects.add(org.project_id));
                
                allProjects.forEach((projectId: string) => {
                    let matchesAllTopics = true;
                    for (const topic of selectedTopics) {
                        if (!projectsByTopic.get(topic)?.has(projectId)) {
                            matchesAllTopics = false;
                            break;
                        }
                    }
                    if (matchesAllTopics) {
                        projectsThatMatchAllTopics.add(projectId);
                    }
                });
            }
        }
        
        // Step 1: Filter organizations by projects that match all topics and by selected countries
        const filteredOrgs = data.filter(org => 
            projectsThatMatchAllTopics.has(org.project_id) &&
            (selectedCountries.length === 0 || selectedCountries.includes(org.country))
        );

        // Step 2: Group by organization name to find unique projects
        const orgProjects = new Map<string, {
            projects: Set<string>,
            orgData: Organization | null,
            totalContribution: number
        }>();
        
        filteredOrgs.forEach(org => {
            if (!orgProjects.has(org.organizationName)) {
                orgProjects.set(org.organizationName, {
                    projects: new Set<string>(),
                    orgData: null,
                    totalContribution: 0
                });
            }
            
            // Add this project to the org's set of projects
            orgProjects.get(org.organizationName)!.projects.add(org.project_id);
            
            // Store the org data (we'll use the first occurrence)
            if (!orgProjects.get(org.organizationName)!.orgData) {
                orgProjects.get(org.organizationName)!.orgData = { ...org };
            }
        });
        
        // Step 3: Create aggregated data with combined project counts and contributions
        const aggregatedData: Organization[] = [];
        
        // Fix TypeScript error by converting Map.entries() to Array and then iterating
        Array.from(orgProjects.entries()).forEach(([orgName, orgInfo]) => {
            if (!orgInfo.orgData) return;
            
            // Calculate total contribution from all projects
            let totalContribution = 0;
            Array.from(orgInfo.projects).forEach((projectId: string) => {
                const project = projectData.get(projectId);
                if (project) {
                    totalContribution += project.ecMaxContribution;
                }
            });
            
            // Create the aggregated organization entry with combined data
            aggregatedData.push({
                ...orgInfo.orgData,
                numofProjects: orgInfo.projects.size,
                totalecContribution: totalContribution,
                // We'll keep topic as the first encountered topic, but we won't display it
            });
        });
        
        // Sort by total contribution and limit to top N
        return aggregatedData
            .sort((a, b) => b.totalecContribution - a.totalecContribution)
            .slice(0, topN);
    }, [data, selectedTopics, selectedCountries, topN, projectData]);

    // Calculate insights without double-counting
    // Use the existing projectsThatMatchAllTopics set from the filteredData calculation
    // This way we ensure we only count projects that match ALL selected topics
    const uniqueProjectIds = React.useMemo(() => {
        // Calculate unique projects that match ALL selected topics
        const uniqueProjects = new Set<string>();
        
        if (selectedTopics.length === 0) {
            // If no topics are selected, include all projects
            data.forEach(org => {
                uniqueProjects.add(org.project_id);
            });
        } else {
            // Group projects by topic
            const projectsByTopic = new Map<string, Set<string>>();
            
            selectedTopics.forEach(topic => {
                projectsByTopic.set(topic, new Set<string>());
            });
            
            // Fill the sets with projects that match each topic
            data.forEach(org => {
                if (selectedTopics.includes(org.topic)) {
                    projectsByTopic.get(org.topic)?.add(org.project_id);
                }
            });
            
            // Find the intersection - projects that exist in ALL topic sets
            if (selectedTopics.length === 1) {
                // If only one topic, just use those projects
                return projectsByTopic.get(selectedTopics[0]) || new Set();
            } else {
                // For each project, check if it exists in all topic sets
                const allProjects = new Set<string>();
                data.forEach(org => allProjects.add(org.project_id));
                
                allProjects.forEach(projectId => {
                    let matchesAllTopics = true;
                    for (const topic of selectedTopics) {
                        if (!projectsByTopic.get(topic)?.has(projectId)) {
                            matchesAllTopics = false;
                            break;
                        }
                    }
                    if (matchesAllTopics) {
                        uniqueProjects.add(projectId);
                    }
                });
            }
        }
        
        // Filter by country if needed
        if (selectedCountries.length > 0) {
            // Find projects in selected countries
            const projectsInSelectedCountries = new Set<string>();
            data.filter(org => selectedCountries.includes(org.country))
                .forEach(org => {
                    projectsInSelectedCountries.add(org.project_id);
                });
            
            // Only keep projects that are both in the topic intersection AND in selected countries
            return new Set(
                Array.from(uniqueProjects).filter(projectId => 
                    projectsInSelectedCountries.has(projectId)
                )
            );
        }
        
        return uniqueProjects;
    }, [data, selectedTopics, selectedCountries]);
    
    // Calculate accurate total contribution from unique projects
    const totalContribution = React.useMemo(() => {
        let total = 0;
        // Fix TypeScript error by explicitly casting array elements to string
        Array.from(uniqueProjectIds).forEach((projectId) => {
            const project = projectData.get(projectId as string);
            if (project) {
                total += project.ecMaxContribution;
            }
        });
        return total;
    }, [uniqueProjectIds, projectData]);
    
    // Use unique project count
    const totalProjects = uniqueProjectIds.size;
    const uniqueCountries = new Set(filteredData.map(org => org.country)).size;

    if (error) {
        return (
            <div className="w-full p-6">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="w-full p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold mb-4">European Research Organizations by Topic</h1>
                
                <div className="flex gap-4 mb-6">
                    <div className="w-1/2">
                        <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-sm font-semibold">Select topic(s):</label>
                                <button
                                    onClick={() => setSelectedTopics(selectedTopics.length === allTopics.length ? [] : allTopics)}
                                    className="text-sm text-blue-600 hover:text-blue-800"
                                >
                                    {selectedTopics.length === allTopics.length ? 'Deselect All' : 'Select All Topics'}
                                </button>
                            </div>
                            {selectedTopics.length > 0 && (
                                <div className="mb-2 flex flex-wrap gap-1">
                                    {selectedTopics.map(topic => (
                                        <span 
                                            key={topic} 
                                            className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs flex items-center"
                                        >
                                            {topic}
                                            <button 
                                                className="ml-1 text-blue-600 hover:text-blue-800"
                                                onClick={() => setSelectedTopics(prev => prev.filter(t => t !== topic))}
                                            >
                                                ×
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            )}
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    placeholder="Search topics..."
                                    value={topicSearch}
                                    onChange={(e) => setTopicSearch(e.target.value)}
                                    className="w-full p-2 border rounded"
                                />
                                <div className="border rounded h-32 overflow-y-auto p-1 bg-white">
                                    {filteredTopics.map(topic => (
                                        <div 
                                            key={topic}
                                            className={`cursor-pointer p-1 rounded hover:bg-blue-100 ${
                                                selectedTopics.includes(topic) ? 'bg-blue-200' : ''
                                            }`}
                                            onClick={() => {
                                                setSelectedTopics(prev => 
                                                    prev.includes(topic) 
                                                        ? prev.filter(t => t !== topic)
                                                        : [...prev, topic]
                                                );
                                            }}
                                            onDoubleClick={() => {
                                                // On double click, make this the only selected topic
                                                setSelectedTopics([topic]);
                                            }}
                                        >
                                            {topic}
                                        </div>
                                    ))}
                                </div>
                                <div className="flex justify-between text-sm text-gray-500">
                                    <span>Click to toggle selection</span>
                                    <span>Double-click to select only this topic</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div className="w-1/2">
                        <div className="mb-4">
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-sm font-semibold">Select country(s):</label>
                                <button
                                    onClick={() => setSelectedCountries(selectedCountries.length === allCountries.length ? [] : allCountries)}
                                    className="text-sm text-blue-600 hover:text-blue-800"
                                >
                                    {selectedCountries.length === allCountries.length ? 'Deselect All' : 'Select All Countries'}
                                </button>
                            </div>
                            {selectedCountries.length > 0 && (
                                <div className="mb-2 flex flex-wrap gap-1">
                                    {selectedCountries.map(country => (
                                        <span 
                                            key={country} 
                                            className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs flex items-center"
                                        >
                                            {country}
                                            <button 
                                                className="ml-1 text-blue-600 hover:text-blue-800"
                                                onClick={() => setSelectedCountries(prev => prev.filter(c => c !== country))}
                                            >
                                                ×
                                            </button>
                                        </span>
                                    ))}
                                </div>
                            )}
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    placeholder="Search countries..."
                                    value={countrySearch}
                                    onChange={(e) => setCountrySearch(e.target.value)}
                                    className="w-full p-2 border rounded"
                                />
                                <div className="border rounded h-32 overflow-y-auto p-1 bg-white">
                                    {filteredCountries.map(country => (
                                        <div 
                                            key={country}
                                            className={`cursor-pointer p-1 rounded hover:bg-blue-100 ${
                                                selectedCountries.includes(country) ? 'bg-blue-200' : ''
                                            }`}
                                            onClick={() => {
                                                setSelectedCountries(prev => 
                                                    prev.includes(country) 
                                                        ? prev.filter(c => c !== country)
                                                        : [...prev, country]
                                                );
                                            }}
                                            onDoubleClick={() => {
                                                // On double click, make this the only selected country
                                                setSelectedCountries([country]);
                                            }}
                                        >
                                            {country}
                                        </div>
                                    ))}
                                </div>
                                <div className="flex justify-between text-sm text-gray-500">
                                    <span>Click to toggle selection</span>
                                    <span>Double-click to select only this country</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Insights Panel */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Total EC Contribution</h3>
                        <p className="text-2xl font-bold text-blue-600">€{totalContribution.toLocaleString()}</p>
                        <p className="text-xs text-gray-500 mt-1">Sum of all unique projects</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Unique Projects</h3>
                        <p className="text-2xl font-bold text-blue-600">{totalProjects}</p>
                        <p className="text-xs text-gray-500 mt-1">Count of distinct projects</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Countries Represented</h3>
                        <p className="text-2xl font-bold text-blue-600">{uniqueCountries}</p>
                    </div>
                </div>
            </div>

                <div className="w-full mb-4">
                    <label className="block text-sm font-semibold mb-2">Top N organizations:</label>
                    <input
                        type="number"
                        min="1"
                        max="100"
                        value={topN}
                        onChange={(e) => setTopN(Number(e.target.value))}
                        className="w-full p-2 border rounded"
                    />
                </div>

            <div className="h-[600px] border rounded-lg overflow-hidden mb-6">
                <MapComponent data={filteredData} />
            </div>
            
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Organization Table</h2>
            </div>

            <div className="mt-6">
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border rounded-lg">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Number of Projects</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total EC Contribution</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {filteredData.map((org, index) => (
                                <tr 
                                    key={index} 
                                    className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50`}
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">{org.organizationName}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{org.country}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{org.numofProjects}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">€{org.totalecContribution.toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}