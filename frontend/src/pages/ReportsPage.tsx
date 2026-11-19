import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Search,
  ExternalLink,
  Inbox,
  Plus
} from 'lucide-react';
import { api } from '../api/client';
import { ConditionBadge, RecommendationBadge } from '../components/common/Badge';

interface ReportsPageProps {
  onNavigateToInspection?: () => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ onNavigateToInspection }) => {
  const [reports, setReports] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadReports() {
      try {
        setIsLoading(true);
        const data = await api.listReports();
        setReports(data);
      } catch (err) {
        console.error('Failed to load reports:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadReports();
  }, []);

  const filtered = reports.filter(r =>
    r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.material_category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.inspector_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-16">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Inspection Reports Library
          </h1>
          <p className="text-gray-500 text-xs mt-1">
            Download certified PDF quality reports containing defect localization, visual evidence, condition classification, and safety disclaimers.
          </p>
        </div>

        {/* Search Input */}
        {reports.length > 0 && (
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search report by ID or material..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white border border-gray-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />
          </div>
        )}
      </div>

      {/* Reports Grid */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-2">
          <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-xs text-gray-500">Loading Reports Archive...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center flex flex-col items-center justify-center shadow-xs">
          <div className="w-12 h-12 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-gray-800">No Inspection Reports Available</h3>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            Certified inspection PDF reports are generated when materials are inspected and saved to inventory.
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((report) => (
            <div
              key={report.id}
              className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs flex flex-col justify-between space-y-4 hover:border-gray-300 transition-colors"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-700">
                      <FileText className="w-4 h-4" />
                    </div>
                    <span className="font-mono text-xs font-bold text-gray-900">{report.id}</span>
                  </div>
                  <ConditionBadge condition={report.condition} size="sm" />
                </div>

                <div>
                  <h3 className="text-sm font-bold text-gray-900">{report.material_category}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[11px] text-gray-500">Recommendation:</span>
                    <RecommendationBadge recommendation={report.recommendation} size="sm" />
                  </div>
                </div>

                <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 text-[11px] space-y-1 text-gray-500 font-mono">
                  <div className="flex items-center justify-between">
                    <span>Inspector:</span>
                    <span className="text-gray-800">{report.inspector_name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Date:</span>
                    <span className="text-gray-800">{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Compliance:</span>
                    <span className="text-emerald-700 font-semibold">ASTM / ISO-9001 Format</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex items-center gap-2">
                <a
                  href={report.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-1.5 px-3 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-1.5 transition-colors shadow-xs"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </a>
                <a
                  href={report.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg border border-gray-200 transition-colors"
                  title="Open in Browser"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
