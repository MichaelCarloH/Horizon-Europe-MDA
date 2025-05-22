'use client'

import React, { useState, useEffect, useMemo } from 'react';
import MultiSelectFilter from './components/MultiSelectFilter';
import ScatterPlot from './components/ScatterPlot';
import BarChart from './components/BarChart';
import LineChart from './components/LineChart';
// import Papa from 'papaparse'; // We'll uncomment this when we add CSV parsing

// Placeholder for data structure - will be refined
interface OrganizationImpactData {
    organizationID: string;
    organizationName: string;
    country: string;
    totalFundingReceived: number;
    numberOfProjectsCoordinated: number;
    averageFundingPerProject: number;
    researchAreas: string[]; // Array of unique topics
    publicationCount: number;
    publicationsPerMillion: number; // Publications per million euros of funding
    publicationYears: number[]; // Years when publications were made
}

interface ProjectData {
    id: number;
    coordinatorID: number;
    coordinatorName: string;
    country: string;
    totalCost: string;
    topic: string;
}

interface PublicationData {
    projectID: string;
    publishedYear: number;
}

type SortField = 'organizationName' | 'country' | 'totalFundingReceived' | 
                 'numberOfProjectsCoordinated' | 'averageFundingPerProject' | 
                 'publicationCount' | 'publicationsPerMillion';
type SortDirection = 'asc' | 'desc';

interface SortConfig {
    field: SortField;
    direction: SortDirection;
}

export default function ResearchImpactMetricsPage() {
    const [allOrganizationsData, setAllOrganizationsData] = useState<OrganizationImpactData[]>([]);
    const [filteredOrganizationsData, setFilteredOrganizationsData] = useState<OrganizationImpactData[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // New state variables for filters and sorting
    const [selectedResearchAreas, setSelectedResearchAreas] = useState<string[]>([]);
    const [researchAreaSearch, setResearchAreaSearch] = useState('');
    const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
    const [countrySearch, setCountrySearch] = useState('');
    const [topN, setTopN] = useState(25);
    const [sortConfig, setSortConfig] = useState<SortConfig>({
        field: 'totalFundingReceived',
        direction: 'desc'
    });

    // Add new state for temporal data
    const [temporalData, setTemporalData] = useState<{
        year: number;
        funding: number;
        publications: number;
    }[]>([]);

    // Add these to the existing state declarations at the top
    const [showAllResearchAreas, setShowAllResearchAreas] = useState(false);
    const [researchAreaTableSearch, setResearchAreaTableSearch] = useState('');
    const [showAllOrganizations, setShowAllOrganizations] = useState(false);
    const [organizationTableSearch, setOrganizationTableSearch] = useState('');
    const [organizationSortConfig, setOrganizationSortConfig] = useState<{
        key: 'organizationName' | 'totalFundingReceived' | 'publicationCount' | 'numberOfProjectsCoordinated' | 'publicationsPerMillion';
        direction: 'asc' | 'desc';
    }>({
        key: 'totalFundingReceived',
        direction: 'desc'
    });
    const [showAllCountriesTable, setShowAllCountriesTable] = useState(false);
    const [countryTableSearch, setCountryTableSearch] = useState('');
    const [countrySortConfig, setCountrySortConfig] = useState<{
        key: 'country' | 'totalFunding' | 'organizations' | 'projects' | 'publications' | 'avgFundingPerOrg';
        direction: 'asc' | 'desc';
    }>({
        key: 'totalFunding',
        direction: 'desc'
    });
    const [scatterPlotSearch, setScatterPlotSearch] = useState('');
    const [expandedResearchAreas, setExpandedResearchAreas] = useState<Set<string>>(new Set());

    useEffect(() => {
        const fetchData = async () => {
            try {
                console.log('Starting to fetch data...');
                // Fetch both project and publication data
                const [projectsResponse, publicationsResponse] = await Promise.all([
                    fetch('/data/project_data_v2.json'),
                    fetch('/data/publications_data.json')
                ]);

                console.log('Project response status:', projectsResponse.status);
                console.log('Publications response status:', publicationsResponse.status);

                if (!projectsResponse.ok || !publicationsResponse.ok) {
                    throw new Error('Failed to fetch data');
                }

                const projectsData: ProjectData[] = await projectsResponse.json();
                const publicationsData: PublicationData[] = await publicationsResponse.json();

                console.log('Loaded projects:', projectsData.length);
                console.log('Loaded publications:', publicationsData.length);

                // Create a map of project ID to coordinator ID
                const projectToCoordinator = new Map(
                    projectsData.map(project => [project.id.toString(), project.coordinatorID.toString()])
                );

                console.log('Project to coordinator mappings:', projectToCoordinator.size);

                // Process the data to aggregate by organization
                const organizationsMap = new Map<string, {
                    organizationName: string;
                    country: string;
                    totalFunding: number;
                    projectCount: number;
                    topics: Set<string>;
                    publications: number;
                    publicationYears: Set<number>;
                }>();

                // First aggregate project data
                projectsData.forEach(project => {
                    const orgId = project.coordinatorID.toString();
                    const currentOrg = organizationsMap.get(orgId);
                    const totalCost = parseFloat(project.totalCost) || 0;
                    const topics = project.topic.split(',').map(t => t.trim()).filter(t => t);

                    if (currentOrg) {
                        currentOrg.totalFunding += totalCost;
                        currentOrg.projectCount += 1;
                        topics.forEach(t => currentOrg.topics.add(t));
                    } else {
                        organizationsMap.set(orgId, {
                            organizationName: project.coordinatorName,
                            country: project.country,
                            totalFunding: totalCost,
                            projectCount: 1,
                            topics: new Set(topics),
                            publications: 0,
                            publicationYears: new Set()
                        });
                    }
                });

                // Then add publication data
                publicationsData.forEach(pub => {
                    const coordinatorId = projectToCoordinator.get(pub.projectID);
                    if (coordinatorId) {
                        const org = organizationsMap.get(coordinatorId);
                        if (org) {
                            org.publications += 1;
                            if (pub.publishedYear) {
                                org.publicationYears.add(pub.publishedYear);
                            }
                        }
                    }
                });

                // Convert Map to array of OrganizationImpactData
                const processedData: OrganizationImpactData[] = Array.from(organizationsMap.entries()).map(([id, org]) => ({
                    organizationID: id,
                    organizationName: org.organizationName,
                    country: org.country,
                    totalFundingReceived: org.totalFunding,
                    numberOfProjectsCoordinated: org.projectCount,
                    averageFundingPerProject: org.totalFunding / org.projectCount,
                    researchAreas: Array.from(org.topics),
                    publicationCount: org.publications,
                    publicationsPerMillion: (org.publications / (org.totalFunding / 1000000)) || 0,
                    publicationYears: Array.from(org.publicationYears).sort()
                }));

                // Sort by total funding (descending) as initial sort
                processedData.sort((a, b) => b.totalFundingReceived - a.totalFundingReceived);

                setAllOrganizationsData(processedData);
                setFilteredOrganizationsData(processedData);
                setIsLoading(false);
            } catch (err) {
                console.error('Error fetching or processing data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load data');
                setIsLoading(false);
            }
        };

        fetchData();
    }, []);

    // Compute unique research areas and countries
    const allResearchAreas = useMemo(() => {
        const areas = new Set<string>();
        allOrganizationsData.forEach(org => {
            org.researchAreas.forEach(area => areas.add(area));
        });
        return Array.from(areas).sort();
    }, [allOrganizationsData]);

    const allCountries = useMemo(() => {
        return Array.from(new Set(allOrganizationsData.map(org => org.country))).sort();
    }, [allOrganizationsData]);

    // Filter and sort data
    useEffect(() => {
        let filtered = [...allOrganizationsData];

        // Apply research area filter
        if (selectedResearchAreas.length > 0) {
            filtered = filtered.filter(org =>
                org.researchAreas.some(area => selectedResearchAreas.includes(area))
            );
        }

        // Apply country filter
        if (selectedCountries.length > 0) {
            filtered = filtered.filter(org =>
                selectedCountries.includes(org.country)
            );
        }

        // Apply sorting
        filtered.sort((a, b) => {
            const aValue = a[sortConfig.field];
            const bValue = b[sortConfig.field];

            if (typeof aValue === 'string' && typeof bValue === 'string') {
                return sortConfig.direction === 'asc'
                    ? aValue.localeCompare(bValue)
                    : bValue.localeCompare(aValue);
            }

            return sortConfig.direction === 'asc'
                ? (aValue as number) - (bValue as number)
                : (bValue as number) - (aValue as number);
        });

        // Apply top N
        filtered = filtered.slice(0, topN);

        setFilteredOrganizationsData(filtered);
    }, [allOrganizationsData, selectedResearchAreas, selectedCountries, sortConfig, topN]);

    // Add temporal data processing in useEffect
    useEffect(() => {
        // Process temporal data
        const yearlyData = allOrganizationsData.reduce((acc, org) => {
            org.publicationYears.forEach(year => {
                if (!acc[year]) {
                    acc[year] = { funding: 0, publications: 0 };
                }
                acc[year].publications++;
                acc[year].funding += org.totalFundingReceived / org.publicationYears.length;
            });
            return acc;
        }, {} as Record<number, { funding: number, publications: number }>);

        setTemporalData(
            Object.entries(yearlyData)
                .map(([year, data]) => ({
                    year: parseInt(year),
                    funding: data.funding,
                    publications: data.publications
                }))
                .sort((a, b) => a.year - b.year)
        );
    }, [allOrganizationsData]);

    const handleSort = (field: SortField) => {
        setSortConfig(current => ({
            field,
            direction: current.field === field && current.direction === 'desc' ? 'asc' : 'desc'
        }));
    };

    if (isLoading) {
        return <div className="p-6">Loading dashboard...</div>;
    }

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
            <h1 className="text-2xl font-bold mb-6">Research Impact Metrics Dashboard</h1>

            {/* Filters Section */}
            <div className="mb-6 p-4 border rounded shadow-sm">
                <h2 className="text-xl font-semibold mb-3">Filters & Controls</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <MultiSelectFilter
                        label="Research Areas"
                        options={allResearchAreas}
                        selectedOptions={selectedResearchAreas}
                        searchTerm={researchAreaSearch}
                        onSearchChange={setResearchAreaSearch}
                        onSelectionChange={setSelectedResearchAreas}
                        onSelectAll={() => setSelectedResearchAreas(allResearchAreas)}
                        onDeselectAll={() => setSelectedResearchAreas([])}
                    />
                    <MultiSelectFilter
                        label="Countries"
                        options={allCountries}
                        selectedOptions={selectedCountries}
                        searchTerm={countrySearch}
                        onSearchChange={setCountrySearch}
                        onSelectionChange={setSelectedCountries}
                        onSelectAll={() => setSelectedCountries(allCountries)}
                        onDeselectAll={() => setSelectedCountries([])}
                    />
                    <div className="col-span-1 md:col-span-2">
                        <label className="block text-sm font-semibold mb-2">
                            Show Top N Organizations:
                        </label>
                        <input
                            type="number"
                            min="1"
                            max="1000"
                            value={topN}
                            onChange={(e) => setTopN(Math.max(1, parseInt(e.target.value) || 25))}
                            className="w-32 p-2 border rounded"
                        />
                    </div>
                </div>
            </div>

            {/* Section 1: Overview and Trends */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Overview and Trends</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-4 border rounded shadow-sm">
                        <div className="mb-4">
                            <input
                                type="text"
                                placeholder="Search organizations..."
                                value={scatterPlotSearch}
                                onChange={(e) => setScatterPlotSearch(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg"
                            />
                        </div>
                        <ScatterPlot
                            data={filteredOrganizationsData
                                .filter(org => org.totalFundingReceived > 1000000)
                                .map(org => ({
                                    x: org.totalFundingReceived,
                                    y: org.publicationCount,
                                    name: org.organizationName,
                                    highlighted: scatterPlotSearch !== '' && 
                                        org.organizationName.toLowerCase().includes(scatterPlotSearch.toLowerCase())
                                }))}
                            title="Publications vs Funding"
                            xLabel="Total Funding (€)"
                            yLabel="Number of Publications"
                            color="#0891b2"
                        />
                    </div>
                    <div className="p-4 border rounded shadow-sm">
                        <LineChart
                            data={temporalData.map(d => ({
                                name: d.year.toString(),
                                value: d.funding
                            }))}
                            title="Funding Distribution Over Time"
                            xLabel="Year"
                            yLabel="Total Funding (€)"
                            color="#f59e0b"
                        />
                    </div>
                    <div className="p-4 border rounded shadow-sm">
                        <LineChart
                            data={temporalData.map(d => ({
                                name: d.year.toString(),
                                value: d.publications
                            }))}
                            title="Publication Output Over Time"
                            xLabel="Year"
                            yLabel="Number of Publications"
                            color="#059669"
                        />
                    </div>
                    <div className="p-4 border rounded shadow-sm">
                        <BarChart
                            data={Object.entries(
                                filteredOrganizationsData.reduce((acc, org) => {
                                    acc[org.country] = (acc[org.country] || 0) + org.totalFundingReceived;
                                    return acc;
                                }, {} as Record<string, number>)
                            )
                                .sort((a, b) => b[1] - a[1])
                                .slice(0, 10)
                                .map(([country, funding]) => ({
                                    name: country,
                                    value: funding
                                }))}
                            title="Top 10 Countries by Total Funding"
                            valueLabel="Total Funding (€)"
                            color="#ec4899"
                        />
                    </div>
                </div>
            </div>

            {/* New Section: Country Analysis */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Country Analysis</h2>
                <div className="p-4 border rounded shadow-sm">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">Country Performance Analysis</h3>
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search countries..."
                                    value={countryTableSearch}
                                    onChange={(e) => setCountryTableSearch(e.target.value)}
                                    className="px-3 py-2 border rounded-lg w-64"
                                />
                                {countryTableSearch && (
                                    <button
                                        onClick={() => setCountryTableSearch('')}
                                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    >
                                        ×
                                    </button>
                                )}
                </div>
                            <button
                                onClick={() => setShowAllCountriesTable(!showAllCountriesTable)}
                                className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                            >
                                {showAllCountriesTable ? 'Show Less' : 'Show All'}
                            </button>
                </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full table-auto">
                        <thead>
                            <tr className="bg-gray-100">
                                <th 
                                    className="px-4 py-2 text-left cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'country',
                                            direction: countrySortConfig.key === 'country' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                >
                                    Country
                                        {countrySortConfig.key === 'country' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                <th 
                                    className="px-4 py-2 text-right cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'totalFunding',
                                            direction: countrySortConfig.key === 'totalFunding' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                >
                                    Total Funding (€)
                                        {countrySortConfig.key === 'totalFunding' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                <th 
                                    className="px-4 py-2 text-right cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'organizations',
                                            direction: countrySortConfig.key === 'organizations' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                    >
                                        Organizations
                                        {countrySortConfig.key === 'organizations' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                <th 
                                    className="px-4 py-2 text-right cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'projects',
                                            direction: countrySortConfig.key === 'projects' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                    >
                                        Projects
                                        {countrySortConfig.key === 'projects' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                <th 
                                    className="px-4 py-2 text-right cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'publications',
                                            direction: countrySortConfig.key === 'publications' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                >
                                    Publications
                                        {countrySortConfig.key === 'publications' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                <th 
                                    className="px-4 py-2 text-right cursor-pointer hover:bg-gray-200"
                                        onClick={() => setCountrySortConfig({
                                            key: 'avgFundingPerOrg',
                                            direction: countrySortConfig.key === 'avgFundingPerOrg' && countrySortConfig.direction === 'asc' ? 'desc' : 'asc'
                                        })}
                                    >
                                        Avg. Funding/Org (€)
                                        {countrySortConfig.key === 'avgFundingPerOrg' && (
                                            <span className="ml-1">{countrySortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                                    )}
                                </th>
                                    <th className="px-4 py-2 text-left">Top Research Areas</th>
                            </tr>
                        </thead>
                        <tbody>
                                {Object.entries(
                                    allOrganizationsData.reduce((acc, org) => {
                                        if (!acc[org.country]) {
                                            acc[org.country] = {
                                                totalFunding: 0,
                                                organizations: new Set(),
                                                projects: 0,
                                                publications: 0,
                                                researchAreas: {} as Record<string, number>
                                            };
                                        }
                                        acc[org.country].totalFunding += org.totalFundingReceived;
                                        acc[org.country].organizations.add(org.organizationID);
                                        acc[org.country].projects += org.numberOfProjectsCoordinated;
                                        acc[org.country].publications += org.publicationCount;
                                        org.researchAreas.forEach(area => {
                                            acc[org.country].researchAreas[area] = (acc[org.country].researchAreas[area] || 0) + 1;
                                        });
                                        return acc;
                                    }, {} as Record<string, {
                                        totalFunding: number;
                                        organizations: Set<string>;
                                        projects: number;
                                        publications: number;
                                        researchAreas: Record<string, number>;
                                    }>)
                                )
                                    .map(([country, data]) => ({
                                        country,
                                        totalFunding: data.totalFunding,
                                        organizations: data.organizations.size,
                                        projects: data.projects,
                                        publications: data.publications,
                                        avgFundingPerOrg: data.totalFunding / data.organizations.size,
                                        topResearchAreas: Object.entries(data.researchAreas)
                                            .sort((a, b) => b[1] - a[1])
                                            .slice(0, 3)
                                            .map(([area]) => area)
                                    }))
                                    .filter(data => 
                                        countryTableSearch === '' || 
                                        data.country.toLowerCase().includes(countryTableSearch.toLowerCase())
                                    )
                                    .sort((a, b) => {
                                        const key = countrySortConfig.key;
                                        const direction = countrySortConfig.direction === 'asc' ? 1 : -1;
                                        
                                        if (key === 'country') {
                                            return direction * a[key].localeCompare(b[key]);
                                        }
                                        
                                        return direction * (a[key] - b[key]);
                                    })
                                    .slice(0, showAllCountriesTable ? undefined : 10)
                                    .map(data => (
                                        <tr key={data.country} className="border-b hover:bg-gray-50">
                                            <td className="px-4 py-2">{data.country}</td>
                                    <td className="px-4 py-2 text-right">
                                                €{data.totalFunding.toLocaleString('en-EU', { maximumFractionDigits: 0 })}
                                    </td>
                                            <td className="px-4 py-2 text-right">{data.organizations}</td>
                                            <td className="px-4 py-2 text-right">{data.projects}</td>
                                            <td className="px-4 py-2 text-right">{data.publications}</td>
                                    <td className="px-4 py-2 text-right">
                                                €{data.avgFundingPerOrg.toLocaleString('en-EU', { maximumFractionDigits: 0 })}
                                    </td>
                                            <td className="px-4 py-2">
                                                <div className="flex flex-wrap gap-1">
                                                    {data.topResearchAreas.map((area, index) => (
                                                        <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                                            {area}
                                            </span>
                                                    ))}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="mt-4 text-sm text-gray-500 flex justify-between items-center">
                        <span>* Click column headers to sort</span>
                        <span className="text-gray-400">
                            {countryTableSearch ? 'Filtered results' : (showAllCountriesTable ? 'Showing all countries' : 'Showing top 10 countries')}
                        </span>
                    </div>
                </div>
            </div>

            {/* Section 2: Research Areas Analysis */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Research Areas Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-4 border rounded shadow-sm">
                        <BarChart
                            data={Object.entries(
                                allOrganizationsData.reduce((acc, org) => {
                                    org.researchAreas.forEach(area => {
                                        acc[area] = (acc[area] || 0) + 1;
                                    });
                                    return acc;
                                }, {} as Record<string, number>)
                            )
                                .sort((a, b) => b[1] - a[1])
                                .slice(0, 10)
                                .map(([area, count]) => ({
                                    name: area.length > 35 ? area.slice(0, 32) + '...' : area,
                                    value: count
                                }))}
                            title="Top 10 Research Areas"
                            valueLabel="Number of Organizations"
                            color="#f59e0b"
                        />
                    </div>
                    <div className="p-4 border rounded shadow-sm">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold">Research Area Funding Analysis</h3>
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder="Search research areas..."
                                        value={researchAreaTableSearch}
                                        onChange={(e) => setResearchAreaTableSearch(e.target.value)}
                                        className="px-3 py-2 border rounded-lg w-64"
                                    />
                                    {researchAreaTableSearch && (
                                        <button
                                            onClick={() => setResearchAreaTableSearch('')}
                                            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                        >
                                            ×
                                        </button>
                                    )}
                                </div>
                                <button
                                    onClick={() => setShowAllResearchAreas(!showAllResearchAreas)}
                                    className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                                >
                                    {showAllResearchAreas ? 'Show Less' : 'Show All'}
                                </button>
                            </div>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full table-auto">
                                <thead>
                                    <tr className="bg-gray-100">
                                        <th className="px-4 py-2 text-left">Research Area</th>
                                        <th className="px-4 py-2 text-right">Total Funding (€)</th>
                                        <th className="px-4 py-2 text-right">Number of Projects</th>
                                        <th className="px-4 py-2 text-right">Avg. Funding per Project (€)</th>
                                        <th className="px-4 py-2 text-right">Organizations</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.entries(
                                        allOrganizationsData.reduce((acc, org) => {
                                            org.researchAreas.forEach(area => {
                                                if (!acc[area]) {
                                                    acc[area] = {
                                                        totalFunding: 0,
                                                        totalProjects: 0,
                                                        organizations: new Set()
                                                    };
                                                }
                                                acc[area].totalFunding += org.totalFundingReceived;
                                                acc[area].totalProjects += org.numberOfProjectsCoordinated;
                                                acc[area].organizations.add(org.organizationID);
                                            });
                                            return acc;
                                        }, {} as Record<string, { 
                                            totalFunding: number; 
                                            totalProjects: number;
                                            organizations: Set<string>;
                                        }>)
                                    )
                                        .map(([area, data]) => ({
                                            name: area,
                                            totalFunding: data.totalFunding,
                                            totalProjects: data.totalProjects,
                                            avgFunding: data.totalFunding / data.totalProjects,
                                            orgCount: data.organizations.size
                                        }))
                                        .sort((a, b) => b.avgFunding - a.avgFunding)
                                        .filter(data => 
                                            researchAreaTableSearch === '' || 
                                            data.name.toLowerCase().includes(researchAreaTableSearch.toLowerCase())
                                        )
                                        .slice(0, showAllResearchAreas ? undefined : 10)
                                        .map(data => (
                                            <tr key={data.name} className="border-b hover:bg-gray-50">
                                                <td className="px-4 py-2">{data.name}</td>
                                                <td className="px-4 py-2 text-right">
                                                    €{data.totalFunding.toLocaleString('en-EU', { maximumFractionDigits: 0 })}
                                    </td>
                                    <td className="px-4 py-2 text-right">
                                                    {data.totalProjects}
                                    </td>
                                                <td className="px-4 py-2 text-right font-semibold">
                                                    €{(data.avgFunding).toLocaleString('en-EU', { maximumFractionDigits: 0 })}
                                                </td>
                                                <td className="px-4 py-2 text-right">
                                                    {data.orgCount}
                                                </td>
                                            </tr>
                                        ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="mt-4 text-sm text-gray-500 flex justify-between items-center">
                            <span>* Sorted by average funding per project in descending order</span>
                            <span className="text-gray-400">
                                {researchAreaTableSearch ? 'Filtered results' : (showAllResearchAreas ? 'Showing all research areas' : 'Showing top 10 research areas')}
                            </span>
                        </div>
                    </div>
                    <div className="p-4 border rounded shadow-sm">
                        <BarChart
                            data={Object.entries(
                                allOrganizationsData.reduce((acc, org) => {
                                    org.researchAreas.forEach(area => {
                                        if (!acc[area]) {
                                            acc[area] = {
                                                totalPublications: 0,
                                                totalYears: 0
                                            };
                                        }
                                        acc[area].totalPublications += org.publicationCount;
                                        acc[area].totalYears += org.publicationYears.length;
                                    });
                                    return acc;
                                }, {} as Record<string, { totalPublications: number; totalYears: number }>)
                            )
                                .map(([area, data]) => ({
                                    name: area.length > 35 ? area.slice(0, 32) + '...' : area,
                                    value: data.totalPublications / data.totalYears
                                }))
                                .sort((a, b) => b.value - a.value)
                                .slice(0, 10)}
                            title="Publication Rate by Research Area"
                            valueLabel="Publications per Year"
                            color="#059669"
                        />
                    </div>
                </div>
            </div>

            {/* Section 3: Organization Performance */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Organization Performance</h2>
                <div className="p-4 border rounded shadow-sm">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">Organization Analysis</h3>
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search organizations..."
                                    value={organizationTableSearch}
                                    onChange={(e) => setOrganizationTableSearch(e.target.value)}
                                    className="px-3 py-2 border rounded-lg w-64"
                                />
                                {organizationTableSearch && (
                                    <button
                                        onClick={() => setOrganizationTableSearch('')}
                                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                                    >
                                        ×
                                    </button>
                                )}
                            </div>
                            <div className="flex items-center gap-2">
                                <label className="text-sm text-gray-600">Show:</label>
                                <input
                                    type="number"
                                    min="5"
                                    max="100"
                                    step="5"
                                    value={showAllOrganizations ? 100 : topN}
                                    onChange={(e) => {
                                        const value = Math.max(5, Math.min(100, parseInt(e.target.value) || 10));
                                        setTopN(value);
                                        setShowAllOrganizations(false);
                                    }}
                                    className="w-20 px-2 py-1 border rounded-lg text-sm"
                                />
                            </div>
                            <button
                                onClick={() => setShowAllOrganizations(!showAllOrganizations)}
                                className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                            >
                                {showAllOrganizations ? 'Show Less' : 'Show All'}
                            </button>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full table-auto">
                            <thead>
                                <tr className="bg-gray-100">
                                    <th className="px-4 py-2 text-left border-b-2 border-gray-200">Organization Info</th>
                                    <th className="px-4 py-2 text-left border-b-2 border-gray-200">Temporal Analysis</th>
                                    <th className="px-4 py-2 text-left border-b-2 border-gray-200">Performance Metrics</th>
                                    <th className="px-4 py-2 text-left border-b-2 border-gray-200">Research Focus</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredOrganizationsData
                                    .filter(org => 
                                        organizationTableSearch === '' || 
                                        org.organizationName.toLowerCase().includes(organizationTableSearch.toLowerCase()) ||
                                        org.country.toLowerCase().includes(organizationTableSearch.toLowerCase())
                                    )
                                    .slice(0, showAllOrganizations ? undefined : topN)
                                    .map(org => {
                                        // Calculate yearly publications for temporal metrics
                                        const yearlyPublications = org.publicationYears.reduce((acc, year) => {
                                            acc[year] = (acc[year] || 0) + 1;
                                            return acc;
                                        }, {} as Record<number, number>);
                                        
                                        const years = Object.keys(yearlyPublications).map(Number).sort();
                                        
                                        // Calculate publication momentum (trend)
                                        let momentum = 'Stable';
                                        if (years.length >= 2) {
                                            const recentYears = years.slice(-2);
                                            const recentPubs = recentYears.map(year => yearlyPublications[year]);
                                            const trend = recentPubs[1] - recentPubs[0];
                                            momentum = trend > 0 ? 'Increasing' : trend < 0 ? 'Decreasing' : 'Stable';
                                        }

                                        // Calculate average publications per year
                                        const avgPublicationsPerYear = years.length > 0 
                                            ? (org.publicationCount / years.length).toFixed(1)
                                            : '0';

                                        // Calculate project success rate (publications per project)
                                        const publicationsPerProject = org.numberOfProjectsCoordinated > 0
                                            ? org.publicationCount / org.numberOfProjectsCoordinated
                                            : 0;

                                        return (
                                            <tr key={org.organizationID} className="border-b hover:bg-gray-50">
                                                <td className="px-4 py-3">
                                                    <div className="flex items-center">
                                                        <div className="flex-1">
                                                            <div className="font-medium">{org.organizationName}</div>
                                                            <div className="flex items-center gap-2 text-xs text-gray-500">
                                                                <span className="bg-gray-100 px-1.5 py-0.5 rounded">{org.country}</span>
                                                                <span className="text-gray-400">·</span>
                                                                <span className="font-mono">ID: {org.organizationID}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="space-y-2">
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Publication Period:</span>
                                                            <span className="font-medium">
                                                                {years.length > 0 ? `${years[0]} - ${years[years.length - 1]}` : 'N/A'}
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Publication Momentum:</span>
                                                            <span className={`font-medium ${
                                                                momentum === 'Increasing' ? 'text-green-600' :
                                                                momentum === 'Decreasing' ? 'text-red-600' :
                                                                'text-yellow-600'
                                                            }`}>
                                                                {momentum} ({avgPublicationsPerYear} pub/year)
                                                            </span>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="space-y-2">
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Success Rate:</span>
                                                            <span className={`font-medium ${
                                                                publicationsPerProject >= 2 ? 'text-green-600' : 
                                                                publicationsPerProject >= 1 ? 'text-yellow-600' : 
                                                                'text-red-600'
                                                            }`}>
                                                                {publicationsPerProject.toFixed(1)} pub/proj
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Impact Density:</span>
                                                            <span className={`font-medium ${
                                                                years.length > 0 && (org.publicationCount / years.length) >= 3 ? 'text-green-600' :
                                                                years.length > 0 && (org.publicationCount / years.length) >= 1 ? 'text-yellow-600' :
                                                                'text-red-600'
                                                            }`}>
                                                                {years.length > 0 ? (org.publicationCount / years.length).toFixed(1) : '0'} pub/year
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Funding Scale:</span>
                                                            <span className="font-medium">
                                                                €{(org.averageFundingPerProject / 1000000).toFixed(1)}M/proj
                                                            </span>
                                                        </div>
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-sm">Project Velocity:</span>
                                                            <span className={`font-medium ${
                                                                years.length > 0 && (org.numberOfProjectsCoordinated / years.length) >= 2 ? 'text-green-600' :
                                                                years.length > 0 && (org.numberOfProjectsCoordinated / years.length) >= 1 ? 'text-yellow-600' :
                                                                'text-red-600'
                                                            }`}>
                                                                {years.length > 0 ? (org.numberOfProjectsCoordinated / years.length).toFixed(1) : '0'} proj/year
                                                            </span>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="space-y-2">
                                                        <div className="flex flex-wrap gap-1">
                                                            {(expandedResearchAreas.has(org.organizationID) 
                                                                ? org.researchAreas 
                                                                : org.researchAreas.slice(0, 3)
                                                            ).map((area, index) => (
                                                                <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                                                    {area}
                                                                </span>
                                                            ))}
                                                            {org.researchAreas.length > 3 && !expandedResearchAreas.has(org.organizationID) && (
                                                                <button
                                                                    onClick={() => setExpandedResearchAreas(prev => {
                                                                        const newSet = new Set(prev);
                                                                        newSet.add(org.organizationID);
                                                                        return newSet;
                                                                    })}
                                                                    className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 rounded border border-blue-200 hover:border-blue-300 bg-blue-50"
                                                                >
                                                                    +{org.researchAreas.length - 3} more
                                                                </button>
                                                            )}
                                                            {expandedResearchAreas.has(org.organizationID) && (
                                                                <button
                                                                    onClick={() => setExpandedResearchAreas(prev => {
                                                                        const newSet = new Set(prev);
                                                                        newSet.delete(org.organizationID);
                                                                        return newSet;
                                                                    })}
                                                                    className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 rounded border border-blue-200 hover:border-blue-300 bg-blue-50"
                                                                >
                                                                    Show Less
                                                                </button>
                                                            )}
                                                        </div>
                                                        <div className="text-sm text-gray-600">
                                                            <span className="font-medium">Research Diversity:</span>{' '}
                                                            {org.researchAreas.length} areas
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                            </tbody>
                        </table>
                    </div>
                    <div className="mt-4 text-sm text-gray-500 flex justify-between items-center">
                        <div className="space-x-4">
                            <span>* Success Rate: Publications per project</span>
                            <span>* Impact Density: Publications per year</span>
                        </div>
                        <span className="text-gray-400">
                            {organizationTableSearch ? 'Filtered results' : (showAllOrganizations ? 'Showing all organizations' : `Showing top ${topN} organizations`)}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
} 