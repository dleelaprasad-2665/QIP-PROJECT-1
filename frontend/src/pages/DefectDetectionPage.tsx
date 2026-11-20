import React, { useState, useEffect } from 'react';
import {
  Crosshair,
  Filter,
  Plus,
  Inbox
} from 'lucide-react';
import { api } from '../api/client';
import type { MaterialInspectionItem } from '../types';
import { ConditionBadge, RecommendationBadge, SeverityBadge } from '../components/common/Badge';

interface DefectDetectionPageProps {
  onNavigateToInspection?: () => void;
}

export const DefectDetectionPage: React.FC<DefectDetectionPageProps> = ({ onNavigateToInspection }) => {
  const [items, setItems] = useState<MaterialInspectionItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<MaterialInspectionItem | null>(null);
  const [activeDefectIndex, setActiveDefectIndex] = useState<number | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('All');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        const data = await api.getInventory({ limit: 50 });
        setItems(data);
        if (data.length > 0) {
          const damaged = data.find(d => d.defect_count > 0) || data[0];
          setSelectedItem(damaged);
        }
      } catch (err) {
        console.error('Failed to load defect items:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-xs text-gray-500 font-medium">Loading Defect Detection Workspace...</span>
      </div>
    );
  }

  // Proper empty state when 0 records exist
  if (items.length === 0 || !selectedItem) {
    return (
      <div className="space-y-6 pb-16">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Defect Detection Workspace
          </h1>
          <p className="text-gray-500 text-xs mt-1">
            Interactive computer vision inspector for localized fractures, corrosion, and structural degradation.
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center flex flex-col items-center justify-center shadow-xs">
          <div className="w-12 h-12 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-gray-800">No Inspected Materials Available</h3>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            No materials have been inspected yet. Complete a material inspection to analyze defects and view bounding boxes in this workspace.
          </p>
          {onNavigateToInspection && (
            <button
              onClick={onNavigateToInspection}
              className="mt-4 inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-3.5 py-2 rounded-lg transition-colors shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Start First Inspection</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  const allDefects = selectedItem.defects || [];
  const filteredDefects = allDefects.filter(d => {
    if (severityFilter === 'All') return true;
    return d.severity === severityFilter;
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Title & Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Defect Detection Workspace
          </h1>
          <p className="text-gray-500 text-xs mt-1">
            Inspect localized defect bounding boxes, surface coordinates, severity ratings, and confidence percentages.
          </p>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 bg-white border border-gray-200 p-1 rounded-lg text-xs shadow-xs">
          <Filter className="w-3.5 h-3.5 text-gray-400 ml-1.5" />
          <span className="text-gray-500 text-xs font-medium mr-1">Severity:</span>
          {['All', 'High', 'Medium', 'Low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-1 rounded font-medium text-xs transition-colors ${
                severityFilter === sev
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Image Canvas (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-xs font-bold text-gray-900">{selectedItem.id}</span>
                <span className="text-xs text-gray-500">• {selectedItem.material_category}</span>
              </div>
              <div className="flex items-center gap-2">
                <ConditionBadge condition={selectedItem.condition} size="sm" />
                <RecommendationBadge recommendation={selectedItem.recommendation} size="sm" />
              </div>
            </div>

            {/* Canvas Viewport with Defect Overlay */}
            <div className="relative rounded-lg overflow-hidden border border-gray-200 bg-black aspect-video flex items-center justify-center">
              <img
                src={api.getImageUrl(selectedItem.annotated_image_path || selectedItem.original_image_path)}
                alt="Defect visual overlay"
                className="w-full h-full object-contain"
              />

              {/* Interactive Bounding Box Overlays */}
              {allDefects.map((d, idx) => {
                if (!d.bbox) return null;
                const isFocused = activeDefectIndex === idx;
                const matchesFilter = severityFilter === 'All' || d.severity === severityFilter;
                if (!matchesFilter) return null;

                const leftPct = (d.bbox.x / 640) * 100;
                const topPct = (d.bbox.y / 480) * 100;
                const widthPct = (d.bbox.width / 640) * 100;
                const heightPct = (d.bbox.height / 480) * 100;

                const borderCol = d.severity === 'High' ? 'border-rose-500' : (d.severity === 'Medium' ? 'border-amber-500' : 'border-blue-500');
                const bgCol = isFocused ? 'bg-blue-500/20 ring-2 ring-blue-500' : 'bg-transparent hover:bg-blue-500/10';

                return (
                  <div
                    key={idx}
                    onMouseEnter={() => setActiveDefectIndex(idx)}
                    onMouseLeave={() => setActiveDefectIndex(null)}
                    style={{
                      left: `${leftPct}%`,
                      top: `${topPct}%`,
                      width: `${widthPct}%`,
                      height: `${heightPct}%`
                    }}
                    className={`absolute cursor-pointer border-2 ${borderCol} ${bgCol} rounded transition-all duration-150 z-20 flex items-start`}
                  >
                    <span className="bg-gray-900/90 text-white font-mono text-[9px] px-1 py-0.5 rounded shadow -translate-y-full whitespace-nowrap">
                      #{idx + 1} {d.name} ({d.confidence}%)
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Bounding Box Legend */}
            <div className="flex items-center justify-between text-xs pt-2 border-t border-gray-100">
              <div className="flex items-center gap-4 text-[11px]">
                <span className="flex items-center gap-1.5 text-rose-700">
                  <span className="w-2 h-2 bg-rose-600 rounded-sm" /> High Severity
                </span>
                <span className="flex items-center gap-1.5 text-amber-700">
                  <span className="w-2 h-2 bg-amber-600 rounded-sm" /> Medium Severity
                </span>
                <span className="flex items-center gap-1.5 text-blue-700">
                  <span className="w-2 h-2 bg-blue-600 rounded-sm" /> Low Severity
                </span>
              </div>
              <span className="text-[11px] text-gray-500 font-mono">
                {filteredDefects.length} Defect Bounding Boxes
              </span>
            </div>
          </div>
        </div>

        {/* Right: Defect Metrics & Material Switcher (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Defect Cards List */}
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-xs space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center justify-between">
              <span>Identified Defects</span>
              <span className="font-mono text-gray-500">{filteredDefects.length} items</span>
            </h3>

            {filteredDefects.length === 0 ? (
              <div className="p-6 rounded-lg bg-gray-50 border border-gray-200 text-center text-gray-500 text-xs">
                No defects matching the selected severity filter.
              </div>
            ) : (
              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                {filteredDefects.map((defect, idx) => {
                  const isFocused = activeDefectIndex === idx;
                  return (
                    <div
                      key={idx}
                      onMouseEnter={() => setActiveDefectIndex(idx)}
                      onMouseLeave={() => setActiveDefectIndex(null)}
                      className={`p-3 rounded-lg border text-xs transition-colors cursor-pointer ${
                        isFocused
                          ? 'bg-blue-50/70 border-blue-300 shadow-xs'
                          : 'bg-gray-50 border-gray-200 hover:bg-gray-100/70'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-blue-600">#{idx + 1}</span>
                          <span className="font-semibold text-gray-900">{defect.name}</span>
                        </div>
                        <SeverityBadge severity={defect.severity} />
                      </div>
                      <p className="text-[11px] text-gray-600 mt-1">{defect.description}</p>
                      <div className="flex items-center justify-between text-[10px] font-mono text-gray-500 mt-2 pt-1.5 border-t border-gray-200">
                        <span>Confidence: <strong className="text-gray-800">{defect.confidence}%</strong></span>
                        {defect.bbox && (
                          <span>Coords: [{defect.bbox.x}, {defect.bbox.y}, {defect.bbox.width}x{defect.bbox.height}]</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Inspection Items Switcher */}
          <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-2 shadow-xs">
            <span className="text-[11px] uppercase font-bold tracking-wider text-gray-500 block">
              Inspected Inventory Materials ({items.length}):
            </span>
            <div className="space-y-1.5 max-h-[200px] overflow-y-auto pr-1">
              {items.map((it) => (
                <button
                  key={it.id}
                  onClick={() => setSelectedItem(it)}
                  className={`w-full p-2 rounded-lg border text-left text-xs flex items-center justify-between transition-colors ${
                    selectedItem.id === it.id
                      ? 'bg-blue-50/70 border-blue-400 text-gray-900 font-semibold'
                      : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <img
                      src={api.getImageUrl(it.original_image_path)}
                      alt={it.material_category}
                      className="w-7 h-7 rounded object-cover border border-gray-200"
                    />
                    <div className="flex flex-col">
                      <span className="font-mono text-xs">{it.id}</span>
                      <span className="text-[10px] text-gray-500">{it.material_category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <ConditionBadge condition={it.condition} size="sm" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
