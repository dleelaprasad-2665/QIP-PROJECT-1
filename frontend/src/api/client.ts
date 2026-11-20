import {
  User,
  AIAnalysisResult,
  MaterialInspectionItem,
  AnalyticsSummary,
  ModelEvaluation
} from '../types';

export function getBackendUrl(): string {
  const custom = typeof window !== 'undefined' ? localStorage.getItem('backend_url') : null;
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/$/, '');
  }
  return (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
}

export function getApiBase(): string {
  const backend = getBackendUrl();
  return backend ? `${backend}/api` : '/api';
}

export function getImageUrl(path: string | null | undefined): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('blob:') || path.startsWith('data:')) {
    return path;
  }
  const backend = getBackendUrl();
  return `${backend}${path.startsWith('/') ? '' : '/'}${path}`;
}

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${getApiBase()}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed. Please check credentials.');
    }
    return res.json();
  },

  async register(data: { username: string; email: string; full_name: string; role: string; password: string }): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${getApiBase()}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Registration failed.');
    }
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${getApiBase()}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error('Failed to fetch user profile.');
    }
    return res.json();
  },

  // AI Inspection
  async analyzeMaterialImage(file: File, site: string, project: string, requestId?: string, signal?: AbortSignal): Promise<AIAnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('site_location', site);
    formData.append('project_name', project);
    if (requestId) {
      formData.append('request_id', requestId);
    }

    const headers: HeadersInit = {
      ...getAuthHeaders(),
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    };

    const res = await fetch(`${getApiBase()}/ai/analyze`, {
      method: 'POST',
      headers,
      body: formData,
      cache: 'no-store',
      signal
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'AI material analysis failed.');
    }
    return res.json();
  },

  async getModelEvaluation(): Promise<ModelEvaluation> {
    const res = await fetch(`${getApiBase()}/ai/evaluation`);
    if (!res.ok) {
      throw new Error('Failed to load model evaluation metrics.');
    }
    return res.json();
  },

  // Inventory
  async getInventory(params?: {
    category?: string;
    condition?: string;
    recommendation?: string;
    site_location?: string;
    status_filter?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<MaterialInspectionItem[]> {
    const query = new URLSearchParams();
    if (params?.category && params.category !== 'All') query.append('category', params.category);
    if (params?.condition && params.condition !== 'All') query.append('condition', params.condition);
    if (params?.recommendation && params.recommendation !== 'All') query.append('recommendation', params.recommendation);
    if (params?.site_location && params.site_location !== 'All') query.append('site_location', params.site_location);
    if (params?.status_filter && params.status_filter !== 'All') query.append('status_filter', params.status_filter);
    if (params?.search) query.append('search', params.search);
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());

    const url = `${getApiBase()}/inventory?${query.toString()}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) {
      throw new Error('Failed to fetch inventory.');
    }
    return res.json();
  },

  async getInventoryItem(id: string): Promise<MaterialInspectionItem> {
    const res = await fetch(`${getApiBase()}/inventory/${id}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error(`Failed to load item ${id}.`);
    }
    return res.json();
  },

  async saveToInventory(data: {
    material_category: string;
    confidence: number;
    condition: string;
    condition_score: number;
    recommendation: string;
    recommendation_reason: string;
    suggested_next_step: string;
    defects: any[];
    original_image_path: string;
    annotated_image_path: string;
    quantity: number;
    unit: string;
    site_location: string;
    project_name: string;
    inspection_status: string;
    notes?: string;
  }): Promise<MaterialInspectionItem> {
    const res = await fetch(`${getApiBase()}/inventory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to save inspection record.');
    }
    return res.json();
  },

  async updateInventoryItem(id: string, data: Partial<MaterialInspectionItem>): Promise<MaterialInspectionItem> {
    const res = await fetch(`${getApiBase()}/inventory/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      throw new Error('Failed to update inventory record.');
    }
    return res.json();
  },

  async deleteInventoryItem(id: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${getApiBase()}/inventory/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error('Failed to delete inventory record.');
    }
    return res.json();
  },

  // Analytics
  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const res = await fetch(`${getApiBase()}/analytics/summary`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error('Failed to fetch analytics.');
    }
    return res.json();
  },

  // Reports
  async listReports(): Promise<{ id: string; material_category: string; condition: string; recommendation: string; created_at: string; inspector_name: string; pdf_url: string }[]> {
    const res = await fetch(`${getApiBase()}/reports/list`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      throw new Error('Failed to fetch reports list.');
    }
    return res.json();
  },

  getPdfReportUrl(id: string): string {
    return `${getApiBase()}/reports/${id}/pdf`;
  },

  getImageUrl(path: string | null | undefined): string {
    return getImageUrl(path);
  }
};
