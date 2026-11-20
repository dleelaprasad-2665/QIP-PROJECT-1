import React, { useState } from 'react';
import {
  Settings,
  Shield,
  Sliders,
  CheckCircle2,
  Save,
  RotateCcw,
  Server,
  Globe
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { RoleBadge } from '../components/common/Badge';
import { getBackendUrl } from '../api/client';

export const SettingsPage: React.FC = () => {
  const { user, switchRoleDemo } = useAuth();

  // Backend API URL configuration
  const [backendUrl, setBackendUrl] = useState(() => getBackendUrl());
  const [urlSaved, setUrlSaved] = useState(false);

  const handleSaveBackendUrl = () => {
    localStorage.setItem('backend_url', backendUrl.trim());
    setUrlSaved(true);
    setTimeout(() => {
      setUrlSaved(false);
      window.location.reload();
    }, 1200);
  };

  // Configurable AI sensitivity parameters
  const [crackThreshold, setCrackThreshold] = useState(18);
  const [rustThreshold, setRustThreshold] = useState(8);
  const [minConfidence, setMinConfidence] = useState(60);
  const [iouThreshold, setIouThreshold] = useState(0.45);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const roleCapabilities = [
    { role: 'Administrator', desc: 'Full system configuration, user role provisioning, database purges, and API access keys.', color: 'text-orange-700' },
    { role: 'Site Engineer', desc: 'Engineering quality sign-offs, reusability validation, and report authorization.', color: 'text-blue-700' },
    { role: 'Inspector', desc: 'Visual field image capture, material upload, preliminary condition screening, and inventory staging.', color: 'text-gray-700' }
  ];

  return (
    <div className="space-y-6 pb-16 max-w-4xl">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-gray-900 tracking-tight">
          Platform Settings & Role Access
        </h1>
        <p className="text-gray-500 text-xs mt-1">
          Manage user credentials, test-drive role permissions, and tune computer vision defect sensitivity thresholds.
        </p>
      </div>

      {/* Backend API Server Configuration */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-600" />
            <span>AI Backend API Server Endpoint</span>
          </h3>
          {urlSaved && (
            <span className="text-xs text-emerald-700 font-mono flex items-center gap-1 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" /> Saved & Reloading...
            </span>
          )}
        </div>

        <p className="text-xs text-gray-500 leading-relaxed">
          Specify the host address of the FastAPI Computer Vision backend (e.g., when hosted on Render or local machine).
        </p>

        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Globe className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              placeholder="e.g. http://localhost:8000 or https://your-backend.onrender.com"
              className="w-full pl-9 pr-3 py-2 text-xs font-mono border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 text-gray-800"
            />
          </div>
          <button
            onClick={handleSaveBackendUrl}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition-colors shadow-xs shrink-0 flex items-center justify-center gap-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save & Connect</span>
          </button>
        </div>
        <p className="text-[11px] text-gray-400">
          Current active endpoint: <strong className="font-mono text-gray-700">{backendUrl || 'Local / Same-Origin (/api)'}</strong>
        </p>
      </div>

      {/* User Profile & Role Permissions */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-xs space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
          <Shield className="w-4 h-4 text-blue-600" />
          <span>Active Session & Role Privileges</span>
        </h3>

        <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-bold text-gray-900 text-sm">{user?.full_name}</span>
              <RoleBadge role={user?.role || 'inspector'} />
            </div>
            <div className="text-xs text-gray-500 font-mono">
              Username: <strong className="text-gray-800">{user?.username}</strong> • Email: <strong className="text-gray-800">{user?.email}</strong>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => switchRoleDemo('admin')}
              className="text-xs bg-white hover:bg-gray-100 text-orange-700 border border-gray-200 px-3 py-1.5 rounded-lg font-medium shadow-xs"
            >
              Simulate Admin
            </button>
            <button
              onClick={() => switchRoleDemo('site_engineer')}
              className="text-xs bg-white hover:bg-gray-100 text-blue-700 border border-gray-200 px-3 py-1.5 rounded-lg font-medium shadow-xs"
            >
              Simulate Engineer
            </button>
            <button
              onClick={() => switchRoleDemo('inspector')}
              className="text-xs bg-white hover:bg-gray-100 text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg font-medium shadow-xs"
            >
              Simulate Inspector
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
          {roleCapabilities.map((rc, idx) => (
            <div key={idx} className="bg-gray-50/70 p-3.5 rounded-lg border border-gray-200 text-xs space-y-1">
              <div className={`font-semibold ${rc.color}`}>{rc.role}</div>
              <p className="text-[11px] text-gray-500 leading-relaxed">{rc.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Computer Vision Sensitivity Sliders */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-xs space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            <span>Computer Vision Detection Thresholds</span>
          </h3>
          {saveSuccess && (
            <span className="text-xs text-emerald-700 font-mono flex items-center gap-1 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" /> Thresholds Updated
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
          {/* Crack Morphological Top-Hat Threshold */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">Crack Top-Hat Sensitivity</label>
              <span className="font-mono text-blue-600 font-bold">{crackThreshold}</span>
            </div>
            <input
              type="range"
              min="5"
              max="40"
              value={crackThreshold}
              onChange={(e) => setCrackThreshold(Number(e.target.value))}
              className="w-full accent-blue-600 bg-gray-200 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-gray-400">Lower values detect faint hairline fissures; higher values filter micro-texture noise.</p>
          </div>

          {/* Rust HSV Segmentation Threshold */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">Corrosion Hue Tolerance</label>
              <span className="font-mono text-blue-600 font-bold">{rustThreshold}</span>
            </div>
            <input
              type="range"
              min="3"
              max="20"
              value={rustThreshold}
              onChange={(e) => setRustThreshold(Number(e.target.value))}
              className="w-full accent-blue-600 bg-gray-200 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-gray-400">Calibrates iron oxide ferric saturation boundary in HSV space.</p>
          </div>

          {/* Minimum Out-of-Domain Confidence */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">Minimum Material Confidence Cutoff</label>
              <span className="font-mono text-blue-600 font-bold">{minConfidence}%</span>
            </div>
            <input
              type="range"
              min="40"
              max="80"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-full accent-blue-600 bg-gray-200 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-gray-400">Rejects non-construction images if primary classifier confidence is below this cutoff.</p>
          </div>

          {/* NMS IoU Overlap Threshold */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-gray-700 font-medium">Bounding Box IoU Suppression</label>
              <span className="font-mono text-blue-600 font-bold">{iouThreshold}</span>
            </div>
            <input
              type="range"
              min="0.2"
              max="0.8"
              step="0.05"
              value={iouThreshold}
              onChange={(e) => setIouThreshold(Number(e.target.value))}
              className="w-full accent-blue-600 bg-gray-200 rounded-lg cursor-pointer"
            />
            <p className="text-[11px] text-gray-400">Eliminates redundant overlapping bounding box proposals.</p>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-3 border-t border-gray-100">
          <button
            onClick={() => {
              setCrackThreshold(18);
              setRustThreshold(8);
              setMinConfidence(60);
              setIouThreshold(0.45);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900 font-medium"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors shadow-xs"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};
