import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  FileText,
  Clock,
  UserCheck,
  Building2,
  Inbox,
  Plus
} from 'lucide-react';
import { api } from '../api/client';
import type { MaterialInspectionItem } from '../types';
import { ConditionBadge, RecommendationBadge } from '../components/common/Badge';

interface InspectionHistoryPageProps {
  onNavigateToInspection?: () => void;
}

export const InspectionHistoryPage: React.FC<InspectionHistoryPageProps> = ({ onNavigateToInspection }) => {
  const [historyItems, setHistoryItems] = useState<MaterialInspectionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCondition, setFilterCondition] = useState('All');

  useEffect(() => {
    async function loadHistory() {
      try {
        setIsLoading(true);
        const data = await api.getInventory({
          condition: filterCondition,
          search: searchQuery,
          limit: 100
        });
        setHistoryItems(data);
      } catch (err) {
        console.error('Failed to load inspection history:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadHistory();
  }, [searchQuery, filterCondition]);

  return (
    <div className="space-y-6 pb-16">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Inspection History & Audit Log
          </h1>
          <p className="text-gray-500 text-xs mt-1">
            Complete audit trail of verified material inspections, computer vision findings, and certified inspection reports.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white border border-gray-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />
          </div>

          <select
            value={filterCondition}
            onChange={(e) => setFilterCondition(e.target.value)}
            aria-label="Filter history by condition"
            className="bg-white border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-blue-600"
          >
            <option value="All">All Conditions</option>
            <option value="GOOD">Good Condition</option>
            <option value="DAMAGED">Damaged</option>
            <option value="INSPECTION REQUIRED">Inspection Required</option>
          </select>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-2">
          <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-xs text-gray-500">Loading History Log...</span>
        </div>
      ) : historyItems.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center flex flex-col items-center justify-center shadow-xs">
          <div className="w-12 h-12 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-gray-800">No History Records Available</h3>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            Inspection history will populate automatically as site materials undergo computer vision quality screening and are saved to inventory.
          </p>
          {onNavigateToInspection && (
            <button
              onClick={onNavigateToInspection}
              className="mt-4 inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-3.5 py-2 rounded-lg transition-colors shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Perform Inspection</span>
            </button>
          )}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 uppercase tracking-wider text-[11px] font-semibold">
                  <th className="py-3 px-4">Inspection ID</th>
                  <th className="py-3 px-4">Image</th>
                  <th className="py-3 px-4">Material Category</th>
                  <th className="py-3 px-4">Condition</th>
                  <th className="py-3 px-4">Recommendation</th>
                  <th className="py-3 px-4">Site Location</th>
                  <th className="py-3 px-4">Inspector</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">PDF Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700 font-medium">
                {historyItems.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-2.5 px-4 font-mono font-semibold text-gray-900">
                      {item.id}
                    </td>
                    <td className="py-2.5 px-4">
                      <img
                        src={api.getImageUrl(item.annotated_image_path || item.original_image_path)}
                        alt={item.material_category}
                        className="w-9 h-9 object-cover rounded border border-gray-200 bg-gray-50"
                      />
                    </td>
                    <td className="py-2.5 px-4 text-gray-900 font-medium">
                      {item.material_category}
                    </td>
                    <td className="py-2.5 px-4">
                      <ConditionBadge condition={item.condition} size="sm" />
                    </td>
                    <td className="py-2.5 px-4">
                      <RecommendationBadge recommendation={item.recommendation} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 text-gray-600">
                      {item.site_location}
                    </td>
                    <td className="py-2.5 px-4 text-gray-600">
                      {item.inspector_name}
                    </td>
                    <td className="py-2.5 px-4 text-gray-500 font-mono text-[11px]">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 text-right">
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
        </div>
      )}
    </div>
  );
};
