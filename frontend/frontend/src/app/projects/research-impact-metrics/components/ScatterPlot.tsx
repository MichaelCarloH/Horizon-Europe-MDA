import React, { useState } from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Label
} from 'recharts';
import PlotModal from './PlotModal';

interface DataPoint {
    x: number;
    y: number;
    name: string;
    highlighted?: boolean;
}

interface ScatterPlotProps {
    data: DataPoint[];
    title: string;
    xLabel: string;
    yLabel: string;
    color: string;
}

const ScatterPlot: React.FC<ScatterPlotProps> = ({ data, title, xLabel, yLabel, color }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const formatValue = (value: number) => {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(1)}K`;
        }
        return value.toString();
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-white p-3 border rounded shadow-lg">
                    <p className="font-semibold">{data.name}</p>
                    <p>{`${xLabel}: ${formatValue(data.x)}`}</p>
                    <p>{`${yLabel}: ${data.y}`}</p>
                </div>
            );
        }
        return null;
    };

    const renderPlot = (containerClassName: string = "h-[400px] w-full") => (
        <div className={containerClassName}>
            <ResponsiveContainer width="100%" height="100%">
                <ScatterChart
                    margin={{
                        top: 20,
                        right: 30,
                        left: 60,
                        bottom: 60
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        type="number"
                        dataKey="x"
                        name={xLabel}
                        tick={{ fontSize: 12 }}
                        domain={[0, (dataMax: number) => Math.ceil(dataMax / 100000000) * 100000000]}
                        tickFormatter={formatValue}
                    >
                        <Label
                            value={xLabel}
                            position="bottom"
                            offset={40}
                            style={{ textAnchor: 'middle', fontSize: 12 }}
                        />
                    </XAxis>
                    <YAxis
                        type="number"
                        dataKey="y"
                        name={yLabel}
                        tick={{ fontSize: 12 }}
                        domain={[0, (dataMax: number) => Math.ceil(dataMax * 1.1)]}
                    >
                        <Label
                            value={yLabel}
                            angle={-90}
                            position="insideLeft"
                            offset={-40}
                            style={{ textAnchor: 'middle', fontSize: 12 }}
                        />
                    </YAxis>
                    <Tooltip content={<CustomTooltip />} />
                    <Scatter
                        data={data.filter(point => !point.highlighted)}
                        fill={color}
                        opacity={0.5}
                    />
                    <Scatter
                        data={data.filter(point => point.highlighted)}
                        fill="#ef4444"
                        opacity={1}
                    />
                </ScatterChart>
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
            {renderPlot()}
            <PlotModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={title}
            >
                {renderPlot("h-full w-full")}
            </PlotModal>
        </div>
    );
};

export default ScatterPlot; 