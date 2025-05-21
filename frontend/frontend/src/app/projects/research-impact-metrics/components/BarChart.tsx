import React, { useState } from 'react';
import {
    BarChart as RechartsBarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import PlotModal from './PlotModal';

interface BarChartProps {
    data: Array<{
        name: string;
        value: number;
    }>;
    title: string;
    valueLabel: string;
    color?: string;
}

export default function BarChart({ data, title, valueLabel, color = "#3b82f6" }: BarChartProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const renderChart = (containerClassName: string = "h-[400px] w-full") => (
        <div className={containerClassName}>
            <ResponsiveContainer width="100%" height="100%">
                <RechartsBarChart
                    data={data}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 40,
                        bottom: 120
                    }}
                    layout="vertical"
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        type="number"
                        tickFormatter={(value) => {
                            if (valueLabel.includes('€')) {
                                return (value / 1000000).toFixed(0) + 'M';
                            }
                            return value.toLocaleString('en-EU');
                        }}
                    />
                    <YAxis
                        dataKey="name"
                        type="category"
                        width={isModalOpen ? 300 : 200}
                        tick={{ fontSize: 11 }}
                    />
                    <Tooltip
                        formatter={(value: number) => [
                            valueLabel.includes('€')
                                ? `€${value.toLocaleString('en-EU', { maximumFractionDigits: 0 })}`
                                : value.toLocaleString('en-EU', { maximumFractionDigits: 2 }),
                            valueLabel
                        ]}
                    />
                    <Bar dataKey="value" fill={color} />
                </RechartsBarChart>
            </ResponsiveContainer>
        </div>
    );

    return (
        <div className="w-full">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">{title}</h3>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="text-blue-600 hover:text-blue-800"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 3h6v6M14 10l6.1-6.1M9 21H3v-6M10 14l-6.1 6.1" />
                    </svg>
                </button>
            </div>
            {renderChart()}
            <PlotModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={title}
            >
                {renderChart("h-full w-full")}
            </PlotModal>
        </div>
    );
} 