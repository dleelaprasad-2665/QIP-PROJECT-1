export type UserRole = 'admin' | 'site_engineer' | 'inspector';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type DefectSeverity = 'Low' | 'Medium' | 'High';

export interface DefectItem {
  name: string;
  severity: DefectSeverity;
  confidence: number;
  bbox?: BoundingBox | null;
  description: string;
}

export type MaterialCondition = 'GOOD' | 'DAMAGED' | 'INSPECTION REQUIRED';
export type RecommendationAction = 'REUSE' | 'INSPECT' | 'REPAIR' | 'RECYCLE' | 'REJECT';

export interface AIAnalysisResult {
  request_id?: string;
  inspection_id?: string;
  is_valid_construction_material: boolean;
  message?: string | null;
  material_category: string;
  material_confidence: number;
  detected_defects: DefectItem[];
  condition: MaterialCondition;
  condition_score: number;
  recommendation: RecommendationAction;
  recommendation_reason: string;
  suggested_next_step: string;
  original_image_url: string;
  annotated_image_url: string;
  inference_time_ms: number;
  safety_disclaimer: string;
}

export interface MaterialInspectionItem {
  id: string;
  original_image_path: string;
  annotated_image_path?: string | null;
  material_category: string;
  confidence: number;
  condition: MaterialCondition;
  condition_score: number;
  recommendation: RecommendationAction;
  recommendation_reason: string;
  suggested_next_step: string;
  defects: DefectItem[];
  defect_count: number;
  quantity: number;
  unit: string;
  site_location: string;
  project_name: string;
  inspection_status: string;
  inspector_name: string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsSummary {
  total_inspected: number;
  total_good: number;
  total_damaged: number;
  total_inspection_required: number;
  total_reuse: number;
  total_repair: number;
  total_recycle: number;
  total_reject: number;
  total_inspect: number;
  estimated_reusable_quantity: number;
  reuse_rate_percentage: number;
  category_distribution: { category: string; count: number }[];
  condition_distribution: { name: string; value: number; color: string }[];
  recommendation_distribution: { name: string; value: number; color: string }[];
  timeline_trend: { date: string; inspections: number; reusable: number; rejected: number }[];
  recent_inspections: MaterialInspectionItem[];
}

export interface ModelEvaluation {
  overall_metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    mAP_50: number;
    mAP_50_95: number;
    avg_inference_time_ms: number;
  };
  class_metrics: {
    material: string;
    precision: number;
    recall: number;
    f1_score: number;
    samples_evaluated: number;
  }[];
  confusion_matrix: {
    labels: string[];
    matrix: number[][];
  };
  defect_detection_metrics: {
    [key: string]: {
      precision: number;
      recall: number;
      f1: number;
      mAP_50: number;
    };
  };
  hardware_info: {
    device: string;
    os: string;
    python_version: string;
    torch_version: string;
    threads: number;
  };
  disclaimer: string;
}
