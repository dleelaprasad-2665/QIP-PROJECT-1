import React, { useEffect, useState } from 'react';
import {
  Boxes,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Recycle,
  Plus,
  FileText,
  Clock,
  ChevronRight,
  TrendingUp,
  Inbox
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
  AreaChart,
  Area
} from 'recharts';
import { api } from '../api/client';
import { AnalyticsSummary, MaterialInspectionItem } from '../types';
import { ConditionBadge, RecommendationBadge } from '../components/common/Badge';

interface DashboardProps {
  onNavigate: (tab: any) => void;
  onSelectItemForInspection?: (item: MaterialInspectionItem) => void;
}

const emptySummary: AnalyticsSummary = {
  total_inspected: 0,
  total_good: 0,
  total_damaged: 0,
  total_inspection_required: 0,
  total_reuse: 0,
  total_repair: 0,
  total_recycle: 0,
  total_reject: 0,
  total_inspect: 0,
  estimated_reusable_quantity: 0,
  reuse_rate_percentage: 0,
  category_distribution: [
    { category: 'Steel', count: 0 },
    { category: 'Bricks', count: 0 },
    { category: 'Cement', count: 0 },
    { category: 'Sand', count: 0 }
  ],
  condition_distribution: [
    { name: 'GOOD', value: 0, color: '#16a34a' },
    { name: 'DAMAGED', value: 0, color: '#dc2626' },
    { name: 'INSPECT', value: 0, color: '#ca8a04' }
  ],
  recommendation_distribution: [
    { name: 'REUSE', value: 0, color: '#16a34a' },
    { name: 'REPAIR', value: 0, color: '#ea580c' },
    { name: 'RECYCLE', value: 0, color: '#2563eb' },
    { name: 'REJECT', value: 0, color: '#dc2626' }
  ],
  timeline_trend: [],
  recent_inspections: []
};

export const DashboardPage: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchSummary() {
      try {
        setIsLoading(true);
        const res = await api.getAnalyticsSummary();
        setData(res);
      } catch (err) {
        console.warn('Backend not reached, showing default dashboard:', err);
        setData(emptySummary);
      } finally {
        setIsLoading(false);
      }
    }
    fetchSummary();
  }, []);

  if (isLoading || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-xs text-gray-500 font-medium">Loading Construction Quality Data...</span>
      </div>
    );
  }

  const hasRecords = data.total_inspected > 0;

  // 5 Compact Statistics Cards
  const kpis = [
    {
      title: 'Total Inspections',
      value: data.total_inspected,
      icon: Boxes,
      iconColor: 'text-blue-600',
      iconBg: 'bg-blue-50 border-blue-100',
      description: 'Total materials audited across sites'
    },
    {
      title: 'Good Materials',
      value: data.total_good,
      icon: CheckCircle2,
      iconColor: 'text-emerald-600',
      iconBg: 'bg-emerald-50 border-emerald-100',
      description: hasRecords ? `${((data.total_good / data.total_inspected) * 100).toFixed(0)}% passing condition` : 'No defects detected'
    },
    {
      title: 'Damaged Materials',
      value: data.total_damaged,
      icon: AlertTriangle,
      iconColor: 'text-rose-600',
      iconBg: 'bg-rose-50 border-rose-100',
      description: 'Requires repair, recycling, or disposal'
    },
    {
      title: 'Inspection Required',
      value: data.total_inspection_required,
      icon: HelpCircle,
      iconColor: 'text-amber-600',
      iconBg: 'bg-amber-50 border-amber-100',
      description: 'Requires engineer verification'
    },
    {
      title: 'Reusable Materials',
      value: data.total_reuse,
      icon: Recycle,
      iconColor: 'text-blue-600',
      iconBg: 'bg-blue-50 border-blue-100',
      description: `${data.estimated_reusable_quantity} units available for reuse`
    }
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Enterprise Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Construction Material Quality & Reusability Dashboard
          </h1>
          <p className="text-gray-500 text-xs mt-1 max-w-2xl">
            Real-time computer vision quality triage, inventory tracking, and circular material reuse management.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => onNavigate('inspection')}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs px-3.5 py-2 rounded-lg shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Inspection</span>
          </button>
          <button
            onClick={() => onNavigate('inventory')}
            className="flex items-center gap-1.5 bg-white hover:bg-gray-50 text-gray-700 font-medium text-xs px-3 py-2 rounded-lg border border-gray-200 transition-colors"
          >
            <Boxes className="w-4 h-4 text-gray-500" />
            <span>View Inventory</span>
          </button>
        </div>
      </div>

      {/* KPI Statistic Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="bg-white border border-gray-200 p-4 rounded-xl flex flex-col justify-between shadow-xs"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-600">{kpi.title}</span>
                <div className={`p-1.5 rounded-lg border ${kpi.iconBg}`}>
                  <Icon className={`w-4 h-4 ${kpi.iconColor}`} />
                </div>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold text-gray-900 font-mono">{kpi.value}</div>
                <div className="text-[11px] text-gray-500 mt-0.5 truncate">{kpi.description}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section: Condition Distribution & Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Material Condition Distribution */}
        <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Material Condition Distribution</h3>
              <p className="text-[11px] text-gray-500">Quality classification breakdown</p>
            </div>
            <span className="text-xs font-mono text-gray-500">{data.total_inspected} items</span>
          </div>

          {!hasRecords ? (
            <div className="h-56 flex flex-col items-center justify-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-2">
                <Inbox className="w-5 h-5" />
              </div>
              <p className="text-xs font-semibold text-gray-700">No condition data recorded</p>
              <p className="text-[11px] text-gray-500 max-w-xs mt-0.5">
                Charts will populate automatically once materials are inspected and stored.
              </p>
            </div>
          ) : (
            <>
              <div className="h-56 relative flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.condition_distribution.filter(d => d.value > 0)}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={78}
                      paddingAngle={3}
                      dataKey="value"
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
                <div className="absolute flex flex-col items-center">
                  <span className="text-lg font-bold font-mono text-gray-900">{data.reuse_rate_percentage}%</span>
                  <span className="text-[10px] text-gray-500 font-medium">Reuse Rate</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-3 border-t border-gray-100 mt-2 text-center">
                {data.condition_distribution.map((item, idx) => (
                  <div key={idx} className="flex flex-col">
                    <span className="text-[11px] text-gray-500 truncate">{item.name.split(' ')[0]}</span>
                    <span className="text-xs font-mono font-bold text-gray-900">{item.value}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Material Category Distribution */}
        <div className="bg-white border border-gray-200 p-5 rounded-xl shadow-xs flex flex-col lg:col-span-2">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Material Categories Audited</h3>
              <p className="text-[11px] text-gray-500">Volume by recognized construction material</p>
            </div>
            {hasRecords && (
              <button
                onClick={() => onNavigate('inventory')}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <span>View Inventory</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {!hasRecords ? (
            <div className="h-56 flex flex-col items-center justify-center text-center p-4">
              <div className="w-10 h-10 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-2">
                <Boxes className="w-5 h-5" />
              </div>
              <p className="text-xs font-semibold text-gray-700">No materials inspected yet</p>
              <p className="text-[11px] text-gray-500 max-w-sm mt-0.5">
                Categories like Concrete, Steel Rebar, Bricks, and Timber will appear in this chart after initial inspections.
              </p>
            </div>
          ) : (
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.category_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis
                    dataKey="category"
                    stroke="#9ca3af"
                    fontSize={11}
                    tickLine={false}
                    angle={-20}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis stroke="#9ca3af" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', borderRadius: '8px', fontSize: '12px', color: '#1f2937' }}
                  />
                  <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Recent Inspections Table */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Recent Material Inspections</h3>
            <p className="text-[11px] text-gray-500">Latest completed quality assessments</p>
          </div>
          {hasRecords && (
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              <span>View All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {!hasRecords ? (
          <div className="p-8 text-center flex flex-col items-center justify-center space-y-2">
            <div className="w-10 h-10 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400">
              <Inbox className="w-5 h-5" />
            </div>
            <p className="text-xs font-medium text-gray-700">
              No materials have been inspected yet. Upload your first construction material image to get started.
            </p>
            <button
              onClick={() => onNavigate('inspection')}
              className="mt-2 inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-3 py-1.5 rounded-lg transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Start New Inspection</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-200 text-gray-500 uppercase tracking-wider text-[11px] bg-gray-50">
                  <th className="py-2.5 px-3">Material ID</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Defects</th>
                  <th className="py-2.5 px-3">Condition</th>
                  <th className="py-2.5 px-3">Recommendation</th>
                  <th className="py-2.5 px-3">Location</th>
                  <th className="py-2.5 px-3">Quantity</th>
                  <th className="py-2.5 px-3 text-right">Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700 font-medium">
                {data.recent_inspections.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-semibold text-gray-900">
                      {item.id}
                    </td>
                    <td className="py-2.5 px-3 text-gray-900 font-medium">
                      {item.material_category}
                    </td>
                    <td className="py-2.5 px-3">
                      {item.defect_count > 0 ? (
                        <span className="text-rose-700 text-[11px] font-mono">
                          {item.defect_count} defect{item.defect_count > 1 ? 's' : ''}
                        </span>
                      ) : (
                        <span className="text-emerald-700 text-[11px] font-mono">Zero Defects</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <ConditionBadge condition={item.condition} size="sm" />
                    </td>
                    <td className="py-2.5 px-3">
                      <RecommendationBadge recommendation={item.recommendation} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-gray-600">
                      {item.site_location}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-gray-800">
                      {item.quantity} {item.unit}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <a
                        href={api.getPdfReportUrl(item.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 px-2 py-1 rounded border border-gray-200 transition-colors"
                      >
                        <FileText className="w-3 h-3 text-blue-600" />
                        <span>PDF</span>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
