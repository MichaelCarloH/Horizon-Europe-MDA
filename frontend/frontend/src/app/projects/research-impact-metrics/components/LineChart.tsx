import React, { useState } from 'react';
import {
    LineChart as RechartsLineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Label
} from 'recharts';
import PlotModal from './PlotModal';

interface LineChartProps {
    data: Array<{
        name: string;
        value: number;
    }>;
    title: string;
    xLabel: string;
    yLabel: string;
    color?: string;
}

export default function LineChart({ data, title, xLabel, yLabel, color = "#3b82f6" }: LineChartProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const renderChart = (containerClassName: string = "h-[400px] w-full") => (
        <div className={containerClassName}>
            <ResponsiveContainer width="100%" height="100%">
                <RechartsLineChart
                    data={data}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 60,
                        bottom: 60
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="name"
                        tick={{ fontSize: 12 }}
                    >
                        <Label
                            value={xLabel}
                            position="bottom"
                            offset={40}
                            style={{ textAnchor: 'middle', fontSize: 12 }}
                        />
                    </XAxis>
                    <YAxis
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => {
                            if (yLabel.includes('€')) {
                                return (value / 1000000).toFixed(0) + 'M';
                            }
                            return value.toLocaleString('en-EU');
                        }}
                    >
                        <Label
                            value={yLabel}
                            angle={-90}
                            position="insideLeft"
                            offset={-40}
                            style={{ textAnchor: 'middle', fontSize: 12 }}
                        />
                    </YAxis>
                    <Tooltip
                        formatter={(value: number) => [
                            yLabel.includes('€')
                                ? `€${value.toLocaleString('en-EU', { maximumFractionDigits: 0 })}`
                                : value.toLocaleString('en-EU', { maximumFractionDigits: 2 }),
                            yLabel
                        ]}
                    />
                    <Line
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                    />
                </RechartsLineChart>
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