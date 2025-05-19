'use client'

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Papa from 'papaparse';

// Dynamically import the map component to avoid SSR issues
const MapComponent = dynamic(() => import('./map-component.tsx'), {
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
}

interface CSVRow {
    organisationID: string;
    organizationName: string;
    country: string;
    numofProjects: string;
    totalecContribution: string;
    latitude: string;
    longitude: string;
    topic: string;
}

export default function OrgMapDashboard() {
    const [data, setData] = useState<Organization[]>([]);
    const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
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
        // Load CSV data
        fetch('/data/org_by_research.csv')
            .then(response => response.text())
            .then(csv => {
                Papa.parse<CSVRow>(csv, {
                    header: true,
                    skipEmptyLines: true,
                    complete: (results) => {
                        try {
                            const parsedData = results.data
                                .filter(row => row.latitude && row.longitude)
                                .map(row => ({
                                    organisationID: String(row.organisationID || ''),
                                    organizationName: String(row.organizationName || ''),
                                    country: String(row.country || ''),
                                    numofProjects: Number(row.numofProjects) || 0,
                                    totalecContribution: Number(row.totalecContribution) || 0,
                                    latitude: Number(row.latitude) || 0,
                                    longitude: Number(row.longitude) || 0,
                                    topic: String(row.topic || '')
                                }));

                            // Get unique topics and countries
                            const topics = Array.from(new Set(parsedData.map(org => org.topic))).filter(Boolean);
                            const countries = Array.from(new Set(parsedData.map(org => org.country))).filter(Boolean).sort();
                            
                            setAllTopics(topics);
                            setAllCountries(countries);
                            setData(parsedData);
                            setError(null);
                        } catch (err) {
                            setError('Error parsing data. Please check the console for details.');
                            console.error('Error parsing data:', err);
                        }
                    },
                    error: (err: Error) => {
                        setError('Error loading data: ' + err.message);
                        console.error('Error loading data:', err);
                    }
                });
            })
            .catch(err => {
                setError('Error fetching data: ' + err.message);
                console.error('Error fetching data:', err);
            });
    }, []);

    // Filter data based on selected topics, countries and top N
    const filteredData = data
        .filter(org => 
            (selectedTopics.length === 0 || selectedTopics.includes(org.topic)) &&
            (selectedCountries.length === 0 || selectedCountries.includes(org.country))
        )
        .sort((a, b) => b.totalecContribution - a.totalecContribution)
        .slice(0, topN);

    // Calculate insights
    const totalContribution = filteredData.reduce((sum, org) => sum + org.totalecContribution, 0);
    const totalProjects = filteredData.reduce((sum, org) => sum + org.numofProjects, 0);
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
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    placeholder="Search topics..."
                                    value={topicSearch}
                                    onChange={(e) => setTopicSearch(e.target.value)}
                                    className="w-full p-2 border rounded"
                                />
                                <select 
                                    multiple
                                    className="w-full p-2 border rounded h-32"
                                    value={selectedTopics}
                                    onChange={(e) => setSelectedTopics(Array.from(e.target.selectedOptions, option => option.value))}
                                >
                                    {filteredTopics.map(topic => (
                                        <option key={topic} value={topic}>{topic}</option>
                                    ))}
                                </select>
                                <p className="text-sm text-gray-500">Hold Ctrl/Cmd to select multiple topics</p>
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
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    placeholder="Search countries..."
                                    value={countrySearch}
                                    onChange={(e) => setCountrySearch(e.target.value)}
                                    className="w-full p-2 border rounded"
                                />
                                <select 
                                    multiple
                                    className="w-full p-2 border rounded h-32"
                                    value={selectedCountries}
                                    onChange={(e) => setSelectedCountries(Array.from(e.target.selectedOptions, option => option.value))}
                                >
                                    {filteredCountries.map(country => (
                                        <option key={country} value={country}>{country}</option>
                                    ))}
                                </select>
                                <p className="text-sm text-gray-500">Hold Ctrl/Cmd to select multiple countries</p>
                            </div>
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

                {/* Insights Panel */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Total EC Contribution</h3>
                        <p className="text-2xl font-bold text-blue-600">€{totalContribution.toLocaleString()}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Total Projects</h3>
                        <p className="text-2xl font-bold text-blue-600">{totalProjects}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <h3 className="text-lg font-semibold text-gray-700">Countries Represented</h3>
                        <p className="text-2xl font-bold text-blue-600">{uniqueCountries}</p>
                    </div>
                </div>
            </div>

            <div className="h-[600px] border rounded-lg overflow-hidden mb-6">
                <MapComponent data={filteredData} />
            </div>

            <div className="mt-6">
                <h2 className="text-xl font-bold mb-4">Organization Table</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border rounded-lg">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Number of Projects</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total EC Contribution</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topic</th>
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
                                    <td className="px-6 py-4 whitespace-nowrap">{org.topic}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
} 