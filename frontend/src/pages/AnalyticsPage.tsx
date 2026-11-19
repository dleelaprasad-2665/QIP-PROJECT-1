import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Recycle,
  Leaf,
  DollarSign,
  Boxes,
  PieChart as PieIcon,
  Inbox,
  Plus
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { api } from '../api/client';
import type { AnalyticsSummary } from '../types';

interface AnalyticsPageProps {
  onNavigateToInspection?: () => void;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ onNavigateToInspection }) => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        setIsLoading(true);
        const res = await api.getAnalyticsSummary();
        setData(res);
      } catch (err) {
        console.error('Failed to load analytics:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadStats();
  }, []);

  if (isLoading || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-xs text-gray-500 font-medium">Loading Material Analytics...</span>
      </div>
    );
  }

  const hasRecords = data.total_inspected > 0;
  const estimatedTonsDiverted = Math.round(data.estimated_reusable_quantity * 0.45);
  const estimatedCO2SavedTons = Math.round(estimatedTonsDiverted * 1.6);
  const estimatedCostSavingsUSD = Math.round(data.estimated_reusable_quantity * 85);

  return (
    <div className="space-y-6 pb-16">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">
          Material Quality & Reusability Analytics
        </h1>
        <p className="text-gray-500 text-xs mt-1">
          Quantitative analytics derived from verified inspection records, circular salvage metrics, and environmental diversion data.
        </p>
      </div>

      {/* Sustainable Construction ROI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Landfill Waste Diverted</span>
            <div className="text-2xl font-bold text-gray-900 font-mono">
              {hasRecords ? `~${estimatedTonsDiverted} tons` : '0 tons'}
            </div>
            <p className="text-[11px] text-gray-500">Diverted through Direct Reuse & Repair</p>
          </div>
          <div className="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-700">
            <Recycle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Embodied Carbon Avoided</span>
            <div className="text-2xl font-bold text-gray-900 font-mono">
              {hasRecords ? `~${estimatedCO2SavedTons} t CO₂e` : '0 t CO₂e'}
            </div>
            <p className="text-[11px] text-gray-500">Avoided virgin material manufacturing emissions</p>
          </div>
          <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-200 text-blue-700">
            <Leaf className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Estimated Cost Savings</span>
            <div className="text-2xl font-bold text-gray-900 font-mono">
              {hasRecords ? `$${estimatedCostSavingsUSD.toLocaleString()}` : '$0'}
            </div>
            <p className="text-[11px] text-gray-500">Secondary material procurement recovery</p>
          </div>
          <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-amber-800">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
      </div>

      {!hasRecords ? (
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center flex flex-col items-center justify-center shadow-xs">
          <div className="w-12 h-12 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-gray-800">No Analytics Data Available</h3>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            Material analytics, circular salvage trajectories, and category trends will appear here once materials are inspected and stored.
          </p>
          {onNavigateToInspection && (
            <button
              onClick={onNavigateToInspection}
              className="mt-4 inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-3.5 py-2 rounded-lg transition-colors shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Inspect First Material</span>
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Row 1 Charts: Category Volume & Condition Triage */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Breakdown */}
            <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex flex-col">
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Material Volume by Category</h3>
                  <p className="text-[11px] text-gray-500">Total units classified and staged across sites</p>
                </div>
                <Boxes className="w-4 h-4 text-blue-600" />
              </div>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.category_distribution} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                    <XAxis type="number" stroke="#9ca3af" fontSize={11} />
                    <YAxis dataKey="category" type="category" stroke="#9ca3af" fontSize={11} width={80} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', fontSize: '12px', color: '#1f2937' }}
                    />
                    <Bar dataKey="count" fill="#2563eb" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Condition Pie Chart */}
            <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex flex-col">
              <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Quality Condition Triage Ratio</h3>
                  <p className="text-[11px] text-gray-500">Distribution between Good, Damaged, and Inspection Required</p>
                </div>
                <PieIcon className="w-4 h-4 text-emerald-600" />
              </div>

              <div className="h-64 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.condition_distribution.filter(d => d.value > 0)}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                      label={({ name, percent }: any) => name ? `${name.split(' ')[0]} ${((percent || 0) * 100).toFixed(0)}%` : ''}
                    >
                      {data.condition_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', fontSize: '12px', color: '#1f2937' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Row 2 Chart: Reuse vs Rejection Trajectory */}
          <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Reuse Salvage vs Rejection Trends</h3>
                <p className="text-[11px] text-gray-500">Tracking daily volume approved for reuse versus rejected materials</p>
              </div>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.timeline_trend} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={11} />
                  <YAxis stroke="#9ca3af" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', fontSize: '12px', color: '#1f2937' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Line type="monotone" dataKey="reusable" stroke="#16a34a" strokeWidth={2} name="Approved for Reuse / Repair" dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="rejected" stroke="#dc2626" strokeWidth={2} name="Rejected / Recycled" dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="inspections" stroke="#2563eb" strokeWidth={1.5} strokeDasharray="4 4" name="Total Inspected" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
