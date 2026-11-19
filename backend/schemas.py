from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth & User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "inspector"  # admin, site_engineer, inspector

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Defect & AI Schemas ---
class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class DefectItem(BaseModel):
    name: str
    severity: str  # Low, Medium, High
    confidence: float  # 0 to 100
    bbox: Optional[BoundingBox] = None
    description: str

class AIAnalysisResult(BaseModel):
    request_id: Optional[str] = None
    inspection_id: Optional[str] = None
    is_valid_construction_material: bool
    message: Optional[str] = None
    material_category: str
    material_confidence: float
    detected_defects: List[DefectItem]
    condition: str  # GOOD, DAMAGED, INSPECTION REQUIRED
    condition_score: float  # 0 to 100
    recommendation: str  # REUSE, INSPECT, REPAIR, RECYCLE, REJECT
    recommendation_reason: str
    suggested_next_step: str
    original_image_url: str
    annotated_image_url: str
    inference_time_ms: float
    safety_disclaimer: str

# --- Material Inspection & Inventory Schemas ---
class MaterialInspectionCreate(BaseModel):
    material_category: str
    confidence: float
    condition: str
    condition_score: float
    recommendation: str
    recommendation_reason: str
    suggested_next_step: str
    defects: List[DefectItem]
    original_image_path: str
    annotated_image_path: str
    quantity: float = 1.0
    unit: str = "pieces"
    site_location: str = "Yard A"
    project_name: str = "EcoBuild 1"
    inspection_status: str = "Verified"
    notes: Optional[str] = None

class MaterialInspectionUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    site_location: Optional[str] = None
    project_name: Optional[str] = None
    inspection_status: Optional[str] = None
    condition: Optional[str] = None
    recommendation: Optional[str] = None
    notes: Optional[str] = None

class MaterialInspectionResponse(BaseModel):
    id: str
    original_image_path: str
    annotated_image_path: Optional[str] = None
    material_category: str
    confidence: float
    condition: str
    condition_score: float
    recommendation: str
    recommendation_reason: str
    suggested_next_step: str
    defects: List[DefectItem]
    defect_count: int
    quantity: float
    unit: str
    site_location: str
    project_name: str
    inspection_status: str
    inspector_name: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Analytics Schemas ---
class AnalyticsSummary(BaseModel):
    total_inspected: int
    total_good: int
    total_damaged: int
    total_inspection_required: int
    total_reuse: int
    total_repair: int
    total_recycle: int
    total_reject: int
    total_inspect: int
    estimated_reusable_quantity: float
    reuse_rate_percentage: float
    category_distribution: List[Dict[str, Any]]
    condition_distribution: List[Dict[str, Any]]
    recommendation_distribution: List[Dict[str, Any]]
    timeline_trend: List[Dict[str, Any]]
    recent_inspections: List[MaterialInspectionResponse]

# --- Model Evaluation Schemas ---
class MetricSummary(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mAP_50: float
    mAP_50_95: float
    avg_inference_time_ms: float

class ClassEvaluation(BaseModel):
    material: str
    precision: float
    recall: float
    f1_score: float
    samples_evaluated: int

class ModelEvaluationResponse(BaseModel):
    overall_metrics: MetricSummary
    class_metrics: List[ClassEvaluation]
    confusion_matrix: Dict[str, Any]
    defect_detection_metrics: Dict[str, Any]
    hardware_info: Dict[str, Any]
    disclaimer: str
