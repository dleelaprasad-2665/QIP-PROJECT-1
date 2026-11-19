import React, { useState, useEffect } from 'react';
import {
  Boxes,
  Search,
  Plus,
  Edit2,
  Trash2,
  FileText,
  Download,
  LayoutGrid,
  Table as TableIcon,
  X,
  Inbox
} from 'lucide-react';
import { api } from '../api/client';
import type { MaterialInspectionItem } from '../types';
import { ConditionBadge, RecommendationBadge } from '../components/common/Badge';

interface MaterialInventoryPageProps {
  onStartNewInspection: () => void;
}

export const MaterialInventoryPage: React.FC<MaterialInventoryPageProps> = ({ onStartNewInspection }) => {
  const [items, setItems] = useState<MaterialInspectionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedCondition, setSelectedCondition] = useState('All');
  const [selectedRecommendation, setSelectedRecommendation] = useState('All');
  const [selectedSite, setSelectedSite] = useState('All');

  // View mode: 'table' as default enterprise view
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');

  // Edit Modal State
  const [editingItem, setEditingItem] = useState<MaterialInspectionItem | null>(null);
  const [editQuantity, setEditQuantity] = useState<number>(1);
  const [editUnit, setEditUnit] = useState<string>('pieces');
  const [editSite, setEditSite] = useState<string>('Central Yard A');
  const [editNotes, setEditNotes] = useState<string>('');
  const [isUpdating, setIsUpdating] = useState(false);

  // Delete confirmation
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const categories = [
    'All',
    'Cement',
    'Bricks',
    'Concrete blocks',
    'Steel rods / Reinforcement bars',
    'Wooden planks',
    'Tiles',
    'Sand',
    'Aggregates',
    'Glass',
    'Pipes'
  ];

  const fetchItems = async () => {
    try {
      setIsLoading(true);
      const data = await api.getInventory({
        category: selectedCategory,
        condition: selectedCondition,
        recommendation: selectedRecommendation,
        site_location: selectedSite,
        search: searchQuery
      });
      setItems(data);
    } catch (err) {
      console.error('Failed to load inventory items:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [selectedCategory, selectedCondition, selectedRecommendation, selectedSite, searchQuery]);

  const handleOpenEdit = (item: MaterialInspectionItem) => {
    setEditingItem(item);
    setEditQuantity(item.quantity);
    setEditUnit(item.unit);
    setEditSite(item.site_location);
    setEditNotes(item.notes || '');
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;
    try {
      setIsUpdating(true);
      await api.updateInventoryItem(editingItem.id, {
        quantity: editQuantity,
        unit: editUnit,
        site_location: editSite,
        notes: editNotes
      });
      setEditingItem(null);
      fetchItems();
    } catch (err) {
      console.error('Failed to update inventory record:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteInventoryItem(id);
      setDeleteId(null);
      fetchItems();
    } catch (err) {
      console.error('Failed to delete item:', err);
    }
  };

  const exportCSV = () => {
    if (items.length === 0) return;
    const headers = ['ID', 'Material Category', 'Condition', 'Score', 'Recommendation', 'Quantity', 'Unit', 'Site Location', 'Defect Count', 'Inspector', 'Date'];
    const rows = items.map(it => [
      it.id,
      `"${it.material_category}"`,
      it.condition,
      it.condition_score,
      it.recommendation,
      it.quantity,
      it.unit,
      `"${it.site_location}"`,
      it.defect_count,
      `"${it.inspector_name}"`,
      new Date(it.created_at).toISOString().split('T')[0]
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `material_inventory_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Title & Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">
            Digital Material Inventory
          </h1>
          <p className="text-gray-500 text-xs mt-1">
            Track, stage, and manage inspected construction materials across yards for potential reuse, repair, recycling, or disposal.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {items.length > 0 && (
            <button
              onClick={exportCSV}
              className="flex items-center gap-1.5 text-xs bg-white hover:bg-gray-50 text-gray-700 font-medium px-3 py-1.5 rounded-lg border border-gray-200 transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5 text-gray-500" />
              <span>Export CSV</span>
            </button>
          )}
          <button
            onClick={onStartNewInspection}
            className="flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-semibold px-3.5 py-1.5 rounded-lg shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Material</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-gray-200 p-4 rounded-xl space-y-3 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 text-xs">
          {/* Search Box */}
          <div className="md:col-span-4 relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by ID, material, location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-gray-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />
          </div>

          {/* Category Filter */}
          <div className="md:col-span-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Filter by material category"
              className="w-full bg-white border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-blue-600"
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c === 'All' ? 'All Categories' : c}</option>
              ))}
            </select>
          </div>

          {/* Condition Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedCondition}
              onChange={(e) => setSelectedCondition(e.target.value)}
              aria-label="Filter by material condition"
              className="w-full bg-white border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-blue-600"
            >
              <option value="All">All Conditions</option>
              <option value="GOOD">Good Condition</option>
              <option value="DAMAGED">Damaged</option>
              <option value="INSPECTION REQUIRED">Inspection Required</option>
            </select>
          </div>

          {/* Recommendation Filter */}
          <div className="md:col-span-2">
            <select
              value={selectedRecommendation}
              onChange={(e) => setSelectedRecommendation(e.target.value)}
              aria-label="Filter by recommendation"
              className="w-full bg-white border border-gray-300 rounded-lg px-2.5 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-blue-600"
            >
              <option value="All">All Recommendations</option>
              <option value="REUSE">Direct Reuse</option>
              <option value="REPAIR">Repair & Reuse</option>
              <option value="INSPECT">Manual Inspect</option>
              <option value="RECYCLE">Recycle Salvage</option>
              <option value="REJECT">Reject / Scrap</option>
            </select>
          </div>

          {/* View Switcher */}
          <div className="md:col-span-1 flex items-center justify-end">
            <div className="flex items-center bg-gray-100 p-0.5 rounded-lg border border-gray-200">
              <button
                onClick={() => setViewMode('table')}
                className={`p-1 rounded transition-colors ${
                  viewMode === 'table' ? 'bg-white text-gray-900 shadow-xs' : 'text-gray-500 hover:text-gray-900'
                }`}
                title="Table View"
              >
                <TableIcon className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={`p-1 rounded transition-colors ${
                  viewMode === 'cards' ? 'bg-white text-gray-900 shadow-xs' : 'text-gray-500 hover:text-gray-900'
                }`}
                title="Grid Cards View"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Results summary line */}
        <div className="flex items-center justify-between text-gray-500 text-[11px] pt-1 border-t border-gray-100">
          <span>Showing <strong className="text-gray-900 font-mono">{items.length}</strong> items in inventory</span>
          {(selectedCategory !== 'All' || selectedCondition !== 'All' || selectedRecommendation !== 'All' || searchQuery) && (
            <button
              onClick={() => {
                setSelectedCategory('All');
                setSelectedCondition('All');
                setSelectedRecommendation('All');
                setSelectedSite('All');
                setSearchQuery('');
              }}
              className="text-blue-600 hover:underline"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-2">
          <div className="w-8 h-8 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-xs text-gray-500">Loading Inventory Records...</span>
        </div>
      ) : items.length === 0 ? (
        /* Empty State */
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center flex flex-col items-center justify-center shadow-xs">
          <div className="w-12 h-12 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-gray-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-gray-800">Inventory Empty</h3>
          <p className="text-xs text-gray-500 max-w-sm mt-1">
            No materials have been inspected yet. Upload your first construction material image to get started.
          </p>
          <button
            onClick={onStartNewInspection}
            className="mt-4 inline-flex items-center gap-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-3.5 py-2 rounded-lg transition-colors shadow-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Upload First Material</span>
          </button>
        </div>
      ) : viewMode === 'table' ? (
        /* Data Table View */
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-gray-50/80 border-b border-gray-200 text-gray-600 uppercase tracking-wider text-[11px] font-semibold">
                  <th className="py-3 px-4">Material ID</th>
                  <th className="py-3 px-4">Image</th>
                  <th className="py-3 px-4">Material Category</th>
                  <th className="py-3 px-4">Condition</th>
                  <th className="py-3 px-4">Quantity</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Recommendation</th>
                  <th className="py-3 px-4">Inspection Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-700 font-medium">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-2.5 px-4 font-mono font-semibold text-gray-900">
                      {item.id}
                    </td>
                    <td className="py-2.5 px-4">
                      <img
                        src={item.annotated_image_path || item.original_image_path}
                        alt={item.material_category}
                        className="w-10 h-10 object-cover rounded border border-gray-200 bg-gray-50"
                      />
                    </td>
                    <td className="py-2.5 px-4 font-medium text-gray-900">
                      {item.material_category}
                    </td>
                    <td className="py-2.5 px-4">
                      <ConditionBadge condition={item.condition} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 font-mono text-gray-900">
                      {item.quantity} {item.unit}
                    </td>
                    <td className="py-2.5 px-4 text-gray-600">
                      {item.site_location}
                    </td>
                    <td className="py-2.5 px-4">
                      <RecommendationBadge recommendation={item.recommendation} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 text-gray-500 text-[11px]">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <a
                          href={api.getPdfReportUrl(item.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded hover:bg-gray-100 text-blue-600"
                          title="Download PDF Report"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </a>
                        <button
                          onClick={() => handleOpenEdit(item)}
                          className="p-1.5 rounded hover:bg-gray-100 text-gray-600 hover:text-gray-900"
                          title="Edit"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setDeleteId(item.id)}
                          className="p-1.5 rounded hover:bg-rose-50 text-gray-400 hover:text-rose-600"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Cards View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-xs hover:border-gray-300 flex flex-col justify-between transition-colors"
            >
              <div>
                <div className="relative aspect-video bg-gray-100 overflow-hidden border-b border-gray-100">
                  <img
                    src={item.annotated_image_path || item.original_image_path}
                    alt={item.material_category}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 left-2">
                    <ConditionBadge condition={item.condition} size="sm" />
                  </div>
                </div>

                <div className="p-4 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold text-gray-900">{item.id}</span>
                    <RecommendationBadge recommendation={item.recommendation} size="sm" />
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-gray-900">{item.material_category}</h3>
                    <p className="text-[11px] text-gray-500 line-clamp-2 mt-0.5">
                      {item.recommendation_reason}
                    </p>
                  </div>

                  <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500 text-[10px] uppercase font-medium">Quantity:</span>
                      <span className="font-mono font-semibold text-gray-900">{item.quantity} {item.unit}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-500 text-[10px] uppercase font-medium">Location:</span>
                      <span className="text-gray-700 text-xs truncate max-w-[140px]">{item.site_location}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="px-4 py-2.5 bg-gray-50/70 border-t border-gray-100 flex items-center justify-between text-xs">
                <a
                  href={api.getPdfReportUrl(item.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>PDF Report</span>
                </a>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleOpenEdit(item)}
                    className="p-1 rounded hover:bg-gray-200 text-gray-600"
                    title="Edit Record"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setDeleteId(item.id)}
                    className="p-1 rounded hover:bg-rose-100 text-gray-400 hover:text-rose-600"
                    title="Delete Record"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingItem && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-gray-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-gray-900">Edit Inventory Record</h3>
                <span className="font-mono text-xs text-blue-600">{editingItem.id}</span>
              </div>
              <button onClick={() => setEditingItem(null)} className="text-gray-400 hover:text-gray-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-600 text-xs font-medium mb-1">Quantity</label>
                  <input
                    type="number"
                    value={editQuantity}
                    onChange={(e) => setEditQuantity(Number(e.target.value))}
                    className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 font-mono focus:outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-gray-600 text-xs font-medium mb-1">Unit</label>
                  <select
                    value={editUnit}
                    onChange={(e) => setEditUnit(e.target.value)}
                    aria-label="Edit unit of measurement"
                    className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-600"
                  >
                    <option value="pieces">pieces</option>
                    <option value="tons">tons</option>
                    <option value="kg">kg</option>
                    <option value="sq.m">sq.m</option>
                    <option value="cu.m">cu.m</option>
                    <option value="meters">meters</option>
                    <option value="bags">bags</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-gray-600 text-xs font-medium mb-1">Site / Yard Location</label>
                <select
                  value={editSite}
                  onChange={(e) => setEditSite(e.target.value)}
                  aria-label="Edit site or yard location"
                  className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-600"
                >
                  <option value="Central Yard A">Central Yard A</option>
                  <option value="Skyline Tower Phase 2">Skyline Tower Phase 2</option>
                  <option value="Metro Rail Extension Yard 4">Metro Rail Extension Yard 4</option>
                  <option value="Harbor Logistic Hub">Harbor Logistic Hub</option>
                  <option value="EcoCity Residential Block B">EcoCity Residential Block B</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-600 text-xs font-medium mb-1">Notes</label>
                <textarea
                  rows={3}
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-gray-900 focus:outline-none focus:border-blue-600"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-200">
              <button
                onClick={() => setEditingItem(null)}
                className="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={isUpdating}
                className="px-3.5 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                {isUpdating ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-xl max-w-sm w-full p-5 space-y-3 shadow-xl">
            <h3 className="text-sm font-bold text-gray-900">Confirm Removal</h3>
            <p className="text-xs text-gray-600">
              Are you sure you want to remove item <strong className="font-mono text-gray-900">{deleteId}</strong> from the inventory?
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDeleteId(null)}
                className="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteId)}
                className="px-3.5 py-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors"
              >
                Delete Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
