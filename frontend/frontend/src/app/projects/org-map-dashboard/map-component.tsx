'use client'

import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import type { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Organization {
    organizationName: string;
    country: string;
    numofProjects: number;
    totalecContribution: number;
    latitude: number;
    longitude: number;
    topic: string;
}

interface MapComponentProps {
    data: Organization[];
}

export default function MapComponent({ data }: MapComponentProps) {
    const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
    const center: LatLngExpression = [54, 15];

    // Calculate marker size based on contribution
    const getMarkerSize = (contribution: number) => {
        return Math.max(8, Math.min(30, Math.sqrt(contribution) / 500));
    };

    return (
        <MapContainer
            center={center}
            zoom={4}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {data.map((org, index) => {
                const position: LatLngExpression = [org.latitude, org.longitude];
                const size = getMarkerSize(org.totalecContribution);
                const isSelected = selectedOrg?.organizationName === org.organizationName;
                
                return (
                    <CircleMarker
                        key={index}
                        center={position}
                        radius={size}
                        pathOptions={{
                            color: isSelected ? '#ff0000' : '#2563eb',
                            fillColor: isSelected ? '#ff0000' : '#3b82f6',
                            fillOpacity: 0.8,
                            weight: isSelected ? 3 : 2,
                            stroke: true,
                            className: 'marker-pulse'
                        }}
                        eventHandlers={{
                            click: () => setSelectedOrg(org),
                            mouseover: (e) => {
                                e.target.setStyle({
                                    fillOpacity: 1,
                                    weight: 3
                                });
                                e.target.openPopup();
                            },
                            mouseout: (e) => {
                                if (!isSelected) {
                                    e.target.setStyle({
                                        fillOpacity: 0.8,
                                        weight: 2
                                    });
                                    e.target.closePopup();
                                }
                            }
                        }}
                    >
                        <Popup
                            position={position}
                            className="custom-popup"
                        >
                            <div className="p-3 min-w-[200px]">
                                <h3 className="font-bold text-lg text-blue-600">{org.organizationName}</h3>
                                <div className="mt-2 space-y-1">
                                    <p><span className="font-semibold text-gray-700">Country:</span> {org.country}</p>
                                    <p><span className="font-semibold text-gray-700">Projects:</span> {org.numofProjects}</p>
                                    <p><span className="font-semibold text-gray-700">EC Contribution:</span> €{org.totalecContribution.toLocaleString()}</p>
                                    <p><span className="font-semibold text-gray-700">Topic:</span> {org.topic}</p>
                                </div>
                            </div>
                        </Popup>
                    </CircleMarker>
                );
            })}
        </MapContainer>
    );
} 