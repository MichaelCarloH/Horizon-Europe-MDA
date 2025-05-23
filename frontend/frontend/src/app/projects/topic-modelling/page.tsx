'use client';
import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import * as Papa from 'papaparse';

const Bar = dynamic(() => import('@ant-design/plots').then(mod => mod.Bar), { ssr: false });
const Area = dynamic(() => import('@ant-design/plots').then(mod => mod.Area), { ssr: false });
const Line = dynamic(() => import('@ant-design/plots').then(mod => mod.Line), { ssr: false });

interface TopicData {
  macro_topic: string;
  num_projects: number;
  total_funding: number;
  avg_funding?: number;
}

interface TemporalData {
  year_quarter: string;
  macro_topic: string;
  num_projects: number;
  total_funding: number;
}

export default function Page() {
  const [macroSummary, setMacroSummary] = useState<TopicData[]>([]);
  const [temporalSummary, setTemporalSummary] = useState<TemporalData[]>([]);

  useEffect(() => {
    const loadCSV = async (url: string): Promise<any[]> => {
      const response = await fetch(url);
      const text = await response.text();
      return new Promise((resolve, reject) => {
        Papa.parse(text, {
          header: true,
          dynamicTyping: true,
          complete: results => resolve(results.data),
          error: (err:Error) => reject(err)
        });
      });
    };

    const fetchData = async () => {
      try {
        const macro = await loadCSV('/data/macro_summary.csv') as TopicData[];
        const temporal = await loadCSV('/data/temporal_summary.csv') as TemporalData[];
        setMacroSummary(macro.filter(d => d.macro_topic && !isNaN(d.total_funding)));
        setTemporalSummary(temporal.filter(d => d.macro_topic && !isNaN(d.total_funding)));
      } catch (err) {
        console.error('Failed to load CSVs:', err);
      }
    };

    fetchData();
  }, []);

  const euro = (val: number) => `€${val.toLocaleString('en-EN', { maximumFractionDigits: 0 })}`;

  const barCommon = {
    legend: false,
    columnStyle: { width: 35 },
    label: {
      position: 'middle',
      style: { fill: '#fff', fontWeight: 500 },
      layout: [{ type: 'adjust-color' }]
    }
  };

  const fundingBar = {
    data: [...macroSummary].sort((a, b) => b.total_funding - a.total_funding),
    xField: 'macro_topic',
    yField: 'total_funding',
    colorField: 'macro_topic',
    xAxis: { title: { text: 'Macro Topic' } },
    yAxis: {
      title: { text: 'Funding (€)' },
      label: { formatter: (v: any) => euro(Number(v)) }
    },
    ...barCommon
  };

  const projectBar = {
    data: [...macroSummary].sort((a, b) => b.num_projects - a.num_projects),
    xField: 'macro_topic',
    yField: 'num_projects',
    colorField: 'macro_topic',
    xAxis: { title: { text: 'Macro Topic' } },
    yAxis: {
      title: { text: 'Projects' },
      label: { formatter: (v: any) => Number(v).toLocaleString() }
    },
    ...barCommon
  };

  const areaProjects = {
    data: temporalSummary,
    xField: 'year_quarter',
    yField: 'num_projects',
    seriesField: 'macro_topic',
    smooth: true,
    xAxis: { label: { rotate: -45 } },
    legend: { position: 'right' },
    colorField: 'macro_topic',
  };

  const areaFunding = {
    data: temporalSummary,
    xField: 'year_quarter',
    yField: 'total_funding',
    seriesField: 'macro_topic',
    smooth: true,
    xAxis: { label: { rotate: -45 } },
    yAxis: { label: { formatter: (val: any) => euro(Number(val)) } },
    legend: { position: 'right' },
    colorField: 'macro_topic',
  };

  return (
    <div className="p-6 space-y-10">
      <div>
        <h2 className="text-xl font-bold">Macro Topics by Total Funding</h2>
        {macroSummary.length > 0 ? <Bar {...fundingBar} /> : <p>Loading funding chart...</p>}
      </div>

      <div>
        <h2 className="text-xl font-bold">Macro Topics by Project Count</h2>
        {macroSummary.length > 0 ? <Bar {...projectBar} /> : <p>Loading project count chart...</p>}
      </div>

      <div>
        <h2 className="text-xl font-bold">Temporal Evolution of Projects</h2>
        {temporalSummary.length > 0 ? <Line {...areaProjects} /> : <p>Loading project evolution chart...</p>}
      </div>

      <div>
        <h2 className="text-xl font-bold">Temporal Evolution of Funding</h2>
        {temporalSummary.length > 0 ? <Line {...areaFunding} /> : <p>Loading funding evolution chart...</p>}
      </div>
    </div>
  );
}

























