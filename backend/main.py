import os
import json
import uuid
import time
import datetime
from pathlib import Path
from typing import Optional, List

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from backend.config import BASE_DIR, UPLOAD_DIR
from backend.database import get_db, Base, engine
from backend.models import User, MaterialInspection, AuditLog
from backend.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    AIAnalysisResult, DefectItem, BoundingBox,
    MaterialInspectionCreate, MaterialInspectionUpdate, MaterialInspectionResponse,
    AnalyticsSummary, ModelEvaluationResponse
)
from backend.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_auth, require_roles
)
from backend.ai_engine import (
    MaterialClassifier, DefectDetector, ConditionRecommender, get_model_evaluation
)
from backend.reports.pdf_generator import generate_pdf_report

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Construction Material Quality Assessment & Reusability Management API",
    description="Intelligent computer vision system for construction material defect detection, condition classification, and circular reuse triage.",
    version="2.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for static image access
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# AI Engines singletons
material_classifier = MaterialClassifier()
defect_detector = DefectDetector()
condition_recommender = ConditionRecommender()


# ------------------ AUTHENTICATION MODULE ------------------

@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        or_(User.username == user_in.username, User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )

    # Validate role
    role = user_in.role.lower()
    if role not in ["admin", "site_engineer", "inspector"]:
        role = "inspector"

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=role,
        hashed_password=get_password_hash(user_in.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.username, "role": new_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your username and password."
        )

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        # Provide default guest inspector profile for quick unauthenticated trial
        return {
            "id": 999,
            "username": "guest_inspector",
            "email": "inspector@constructionsite.com",
            "full_name": "Field Quality Inspector (Demo Session)",
            "role": "site_engineer",
            "is_active": True,
            "created_at": datetime.datetime.utcnow()
        }
    return current_user


# ------------------ AI COMPUTER VISION MODULE ------------------

@app.post("/api/ai/analyze", response_model=AIAnalysisResult)
async def analyze_material_image(
    response: Response,
    file: UploadFile = File(...),
    request_id: Optional[str] = Form(None),
    site_location: Optional[str] = Form("Central Yard A"),
    project_name: Optional[str] = Form("EcoBuild Site 1"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Set explicit non-caching headers for every prediction request
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    start_time = time.time()
    actual_request_id = request_id or f"req_{uuid.uuid4().hex[:12]}"

    # Read image contents directly from upload stream
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None or img_bgr.size == 0:
        raise HTTPException(status_code=400, detail="Invalid or unsupported image file format.")

    original_filename = f"orig_{actual_request_id}_{file.filename.replace(' ', '_')}"
    original_filepath = UPLOAD_DIR / original_filename

    # Save original image with unique request ID
    with open(original_filepath, "wb") as f:
        f.write(contents)

    # 1. Independent Material Identification (Strictly based on image pixels, no filename hints)
    classification_result = material_classifier.predict(img_bgr)

    if not classification_result["is_valid"]:
        # Image is not a valid construction material, low confidence, or too blurry/unclear
        inference_time = round((time.time() - start_time) * 1000, 2)
        return {
            "request_id": actual_request_id,
            "is_valid_construction_material": False,
            "message": classification_result["message"],
            "material_category": classification_result["category"],
            "material_confidence": classification_result["confidence"],
            "detected_defects": [],
            "condition": "INSPECTION REQUIRED",
            "condition_score": 0.0,
            "recommendation": "INSPECT",
            "recommendation_reason": "Visual screening confidence is insufficient for automated triage.",
            "suggested_next_step": "Please upload a clearer image or request manual inspection.",
            "original_image_url": f"/uploads/{original_filename}",
            "annotated_image_url": f"/uploads/{original_filename}",
            "inference_time_ms": inference_time,
            "safety_disclaimer": "Automated Computer Vision screening failed sanity checks or confidence threshold."
        }

    category = classification_result["category"]
    mat_conf = classification_result["confidence"]

    # 2. Defect Detection on this exact newly uploaded image
    defects, annotated_bgr = defect_detector.detect_defects(img_bgr, category)

    annotated_filename = f"annot_{actual_request_id}_{file.filename.replace(' ', '_')}"
    annotated_filepath = UPLOAD_DIR / annotated_filename
    cv2.imwrite(str(annotated_filepath), annotated_bgr)

    # 3. Condition Classification & Recommendation
    eval_res = condition_recommender.evaluate(
        material_category=category,
        material_confidence=mat_conf,
        defects=defects
    )

    inference_time = round((time.time() - start_time) * 1000, 2)

    # Convert defects to Pydantic objects
    defect_items = []
    for d in defects:
        bbox_obj = None
        if "bbox" in d and d["bbox"]:
            bbox_obj = BoundingBox(
                x=d["bbox"]["x"],
                y=d["bbox"]["y"],
                width=d["bbox"]["width"],
                height=d["bbox"]["height"]
            )
        defect_items.append(
            DefectItem(
                name=d["name"],
                severity=d["severity"],
                confidence=d["confidence"],
                bbox=bbox_obj,
                description=d.get("description", "")
            )
        )

    # Auto-persist inspection record directly linked to this exact upload
    date_prefix = datetime.datetime.utcnow().strftime("%Y%m%d")
    rand_code = uuid.uuid4().hex[:4].upper()
    inspection_id = f"MAT-{date_prefix}-{rand_code}"

    inspector_name = current_user.full_name if current_user else "Field Inspector"
    inspector_id = current_user.id if current_user else None
    defects_dict = [d.dict() for d in defect_items]

    unit_map = {
        "Cement": "bags",
        "Steel rods / Reinforcement bars": "tons",
        "Tiles": "sq.m",
        "Pipes": "meters",
        "Sand": "cu.m",
        "Aggregates": "cu.m",
        "Bricks": "pieces",
        "Wooden planks": "pieces",
        "Concrete blocks": "pieces",
        "Glass": "panels"
    }
    unit_val = unit_map.get(category, "pieces")

    new_item = MaterialInspection(
        id=inspection_id,
        original_image_path=f"/uploads/{original_filename}",
        annotated_image_path=f"/uploads/{annotated_filename}",
        material_category=category,
        confidence=mat_conf,
        condition=eval_res["condition"],
        condition_score=eval_res["condition_score"],
        recommendation=eval_res["recommendation"],
        recommendation_reason=eval_res["recommendation_reason"],
        suggested_next_step=eval_res["suggested_next_step"],
        defects_json=json.dumps(defects_dict),
        defect_count=len(defects_dict),
        quantity=1.0,
        unit=unit_val,
        site_location=site_location or "Central Yard A",
        project_name=project_name or "EcoBuild Site 1",
        inspection_status="Verified" if eval_res["condition"] == "GOOD" else "Pending Review",
        inspector_id=inspector_id,
        inspector_name=inspector_name,
        notes=f"Automated AI screening from upload {actual_request_id}.",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(new_item)

    audit = AuditLog(
        action="INSPECTION_CREATED",
        entity_type="MATERIAL_INSPECTION",
        entity_id=inspection_id,
        user_id=inspector_id,
        user_name=inspector_name,
        details=f"Automated AI quality inspection for {category} ({eval_res['condition']})."
    )
    db.add(audit)
    db.commit()
    db.refresh(new_item)

    return {
        "request_id": actual_request_id,
        "inspection_id": inspection_id,
        "is_valid_construction_material": True,
        "message": None,
        "material_category": category,
        "material_confidence": mat_conf,
        "detected_defects": defect_items,
        "condition": eval_res["condition"],
        "condition_score": eval_res["condition_score"],
        "recommendation": eval_res["recommendation"],
        "recommendation_reason": eval_res["recommendation_reason"],
        "suggested_next_step": eval_res["suggested_next_step"],
        "original_image_url": f"/uploads/{original_filename}",
        "annotated_image_url": f"/uploads/{annotated_filename}",
        "inference_time_ms": inference_time,
        "safety_disclaimer": eval_res["safety_disclaimer"]
    }


# ------------------ DIGITAL INVENTORY MODULE ------------------

def parse_inspection_model(insp: MaterialInspection) -> dict:
    try:
        defects_raw = json.loads(insp.defects_json) if insp.defects_json else []
    except Exception:
        defects_raw = []

    defects = []
    for d in defects_raw:
        bbox_obj = None
        if "bbox" in d and d["bbox"]:
            bbox_obj = BoundingBox(
                x=d["bbox"].get("x", 0),
                y=d["bbox"].get("y", 0),
                width=d["bbox"].get("width", 0),
                height=d["bbox"].get("height", 0)
            )
        defects.append(
            DefectItem(
                name=d.get("name", "Defect"),
                severity=d.get("severity", "Medium"),
                confidence=d.get("confidence", 80.0),
                bbox=bbox_obj,
                description=d.get("description", "")
            )
        )

    return {
        "id": insp.id,
        "original_image_path": insp.original_image_path,
        "annotated_image_path": insp.annotated_image_path,
        "material_category": insp.material_category,
        "confidence": insp.confidence,
        "condition": insp.condition,
        "condition_score": insp.condition_score,
        "recommendation": insp.recommendation,
        "recommendation_reason": insp.recommendation_reason,
        "suggested_next_step": insp.suggested_next_step,
        "defects": defects,
        "defect_count": insp.defect_count,
        "quantity": insp.quantity,
        "unit": insp.unit,
        "site_location": insp.site_location,
        "project_name": insp.project_name,
        "inspection_status": insp.inspection_status,
        "inspector_name": insp.inspector_name,
        "notes": insp.notes,
        "created_at": insp.created_at,
        "updated_at": insp.updated_at
    }

@app.get("/api/inventory", response_model=List[MaterialInspectionResponse])
def get_inventory(
    category: Optional[str] = None,
    condition: Optional[str] = None,
    recommendation: Optional[str] = None,
    site_location: Optional[str] = None,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(MaterialInspection)

    if category and category != "All":
        query = query.filter(MaterialInspection.material_category == category)
    if condition and condition != "All":
        query = query.filter(MaterialInspection.condition == condition)
    if recommendation and recommendation != "All":
        query = query.filter(MaterialInspection.recommendation == recommendation)
    if site_location and site_location != "All":
        query = query.filter(MaterialInspection.site_location == site_location)
    if status_filter and status_filter != "All":
        query = query.filter(MaterialInspection.inspection_status == status_filter)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                MaterialInspection.id.ilike(search_fmt),
                MaterialInspection.material_category.ilike(search_fmt),
                MaterialInspection.site_location.ilike(search_fmt),
                MaterialInspection.project_name.ilike(search_fmt),
                MaterialInspection.inspector_name.ilike(search_fmt),
                MaterialInspection.notes.ilike(search_fmt)
            )
        )

    records = query.order_by(desc(MaterialInspection.created_at)).offset(offset).limit(limit).all()
    return [parse_inspection_model(r) for r in records]

@app.get("/api/inventory/{item_id}", response_model=MaterialInspectionResponse)
def get_inventory_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(MaterialInspection).filter(MaterialInspection.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Material inspection '{item_id}' not found.")
    return parse_inspection_model(item)

@app.post("/api/inventory", response_model=MaterialInspectionResponse)
def create_inventory_item(
    item_in: MaterialInspectionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    inspector_name = current_user.full_name if current_user else "Field Inspector"
    inspector_id = current_user.id if current_user else None

    # Check if this exact inspection record already exists (e.g. created during /api/ai/analyze)
    existing = db.query(MaterialInspection).filter(
        MaterialInspection.original_image_path == item_in.original_image_path
    ).first()

    if existing:
        existing.quantity = item_in.quantity
        existing.unit = item_in.unit
        existing.site_location = item_in.site_location
        existing.project_name = item_in.project_name
        existing.notes = item_in.notes
        if inspector_name:
            existing.inspector_name = inspector_name
        existing.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return parse_inspection_model(existing)

    # Generate unique ID: MAT-YYYYMMDD-XXXX
    date_prefix = datetime.datetime.utcnow().strftime("%Y%m%d")
    rand_code = uuid.uuid4().hex[:4].upper()
    new_id = f"MAT-{date_prefix}-{rand_code}"

    # Convert defects list to json
    defects_dict = [d.dict() for d in item_in.defects]

    new_item = MaterialInspection(
        id=new_id,
        original_image_path=item_in.original_image_path,
        annotated_image_path=item_in.annotated_image_path,
        material_category=item_in.material_category,
        confidence=item_in.confidence,
        condition=item_in.condition,
        condition_score=item_in.condition_score,
        recommendation=item_in.recommendation,
        recommendation_reason=item_in.recommendation_reason,
        suggested_next_step=item_in.suggested_next_step,
        defects_json=json.dumps(defects_dict),
        defect_count=len(defects_dict),
        quantity=item_in.quantity,
        unit=item_in.unit,
        site_location=item_in.site_location,
        project_name=item_in.project_name,
        inspection_status=item_in.inspection_status,
        inspector_id=inspector_id,
        inspector_name=inspector_name,
        notes=item_in.notes,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    db.add(new_item)

    # Log audit
    audit = AuditLog(
        action="INSPECTION_CREATED",
        entity_type="MATERIAL_INSPECTION",
        entity_id=new_id,
        user_id=inspector_id,
        user_name=inspector_name,
        details=f"Inspected {item_in.material_category} ({item_in.condition}) at {item_in.site_location}."
    )
    db.add(audit)

    db.commit()
    db.refresh(new_item)
    return parse_inspection_model(new_item)

@app.put("/api/inventory/{item_id}", response_model=MaterialInspectionResponse)
def update_inventory_item(
    item_id: str,
    update_data: MaterialInspectionUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    item = db.query(MaterialInspection).filter(MaterialInspection.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    for field, val in update_data.dict(exclude_unset=True).items():
        if val is not None:
            setattr(item, field, val)

    item.updated_at = datetime.datetime.utcnow()

    audit = AuditLog(
        action="INSPECTION_UPDATED",
        entity_type="MATERIAL_INSPECTION",
        entity_id=item_id,
        user_id=current_user.id if current_user else None,
        user_name=current_user.full_name if current_user else "System",
        details=f"Updated item {item_id}."
    )
    db.add(audit)

    db.commit()
    db.refresh(item)
    return parse_inspection_model(item)

@app.delete("/api/inventory/{item_id}")
def delete_inventory_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    item = db.query(MaterialInspection).filter(MaterialInspection.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    db.delete(item)

    audit = AuditLog(
        action="INSPECTION_DELETED",
        entity_type="MATERIAL_INSPECTION",
        entity_id=item_id,
        user_id=current_user.id if current_user else None,
        user_name=current_user.full_name if current_user else "System",
        details=f"Deleted inspection record {item_id}."
    )
    db.add(audit)

    db.commit()
    return {"success": True, "message": f"Material inspection '{item_id}' deleted successfully."}


# ------------------ ANALYTICS DASHBOARD MODULE ------------------

@app.get("/api/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Computes real-time dynamic statistics and time-series trends directly from database records.
    """
    total_inspected = db.query(MaterialInspection).count()
    if total_inspected == 0:
        return {
            "total_inspected": 0,
            "total_good": 0,
            "total_damaged": 0,
            "total_inspection_required": 0,
            "total_reuse": 0,
            "total_repair": 0,
            "total_recycle": 0,
            "total_reject": 0,
            "total_inspect": 0,
            "estimated_reusable_quantity": 0.0,
            "reuse_rate_percentage": 0.0,
            "category_distribution": [],
            "condition_distribution": [],
            "recommendation_distribution": [],
            "timeline_trend": [],
            "recent_inspections": []
        }

    # Condition counts
    total_good = db.query(MaterialInspection).filter(MaterialInspection.condition == "GOOD").count()
    total_damaged = db.query(MaterialInspection).filter(MaterialInspection.condition == "DAMAGED").count()
    total_inspection_required = db.query(MaterialInspection).filter(MaterialInspection.condition == "INSPECTION REQUIRED").count()

    # Recommendation counts
    total_reuse = db.query(MaterialInspection).filter(MaterialInspection.recommendation == "REUSE").count()
    total_repair = db.query(MaterialInspection).filter(MaterialInspection.recommendation == "REPAIR").count()
    total_recycle = db.query(MaterialInspection).filter(MaterialInspection.recommendation == "RECYCLE").count()
    total_reject = db.query(MaterialInspection).filter(MaterialInspection.recommendation == "REJECT").count()
    total_inspect = db.query(MaterialInspection).filter(MaterialInspection.recommendation == "INSPECT").count()

    # Estimated reusable quantity (items marked REUSE or REPAIR)
    reusable_items = db.query(MaterialInspection).filter(
        MaterialInspection.recommendation.in_(["REUSE", "REPAIR"])
    ).all()
    est_reusable_qty = sum(item.quantity for item in reusable_items)
    reuse_rate = round(((total_reuse + total_repair) / total_inspected) * 100, 1)

    # Category distribution
    cat_counts = db.query(
        MaterialInspection.material_category,
        func.count(MaterialInspection.id).label("count")
    ).group_by(MaterialInspection.material_category).all()
    category_distribution = [{"category": row[0], "count": row[1]} for row in cat_counts]

    # Condition distribution
    condition_distribution = [
        {"name": "Good Condition", "value": total_good, "color": "#16A34A"},
        {"name": "Damaged", "value": total_damaged, "color": "#DC2626"},
        {"name": "Inspection Required", "value": total_inspection_required, "color": "#D97706"},
    ]

    # Recommendation distribution
    recommendation_distribution = [
        {"name": "Direct Reuse", "value": total_reuse, "color": "#16A34A"},
        {"name": "Repair & Reuse", "value": total_repair, "color": "#0284C7"},
        {"name": "Physical Inspect", "value": total_inspect, "color": "#D97706"},
        {"name": "Recycle Recovery", "value": total_recycle, "color": "#7C3AED"},
        {"name": "Reject / Scrap", "value": total_reject, "color": "#DC2626"},
    ]

    # Timeline trend (inspections grouped by day for last 14 days)
    inspections = db.query(MaterialInspection).order_by(MaterialInspection.created_at.asc()).all()
    trend_dict = {}
    for insp in inspections:
        day_str = insp.created_at.strftime("%b %d")
        if day_str not in trend_dict:
            trend_dict[day_str] = {"date": day_str, "inspections": 0, "reusable": 0, "rejected": 0}
        trend_dict[day_str]["inspections"] += 1
        if insp.recommendation in ["REUSE", "REPAIR"]:
            trend_dict[day_str]["reusable"] += 1
        elif insp.recommendation in ["REJECT", "RECYCLE"]:
            trend_dict[day_str]["rejected"] += 1

    timeline_trend = list(trend_dict.values())[-10:]

    # Recent inspections
    recent_records = db.query(MaterialInspection).order_by(desc(MaterialInspection.created_at)).limit(6).all()
    recent_inspections = [parse_inspection_model(r) for r in recent_records]

    return {
        "total_inspected": total_inspected,
        "total_good": total_good,
        "total_damaged": total_damaged,
        "total_inspection_required": total_inspection_required,
        "total_reuse": total_reuse,
        "total_repair": total_repair,
        "total_recycle": total_recycle,
        "total_reject": total_reject,
        "total_inspect": total_inspect,
        "estimated_reusable_quantity": round(est_reusable_qty, 2),
        "reuse_rate_percentage": reuse_rate,
        "category_distribution": category_distribution,
        "condition_distribution": condition_distribution,
        "recommendation_distribution": recommendation_distribution,
        "timeline_trend": timeline_trend,
        "recent_inspections": recent_inspections
    }


# ------------------ INSPECTION PDF REPORTS MODULE ------------------

@app.get("/api/reports/{item_id}/pdf")
def download_pdf_report(item_id: str, db: Session = Depends(get_db)):
    item = db.query(MaterialInspection).filter(MaterialInspection.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Inspection report '{item_id}' not found.")

    pdf_filename = f"Inspection_Report_{item_id}.pdf"
    pdf_path = UPLOAD_DIR / pdf_filename

    # Always generate fresh high-resolution report
    item_dict = parse_inspection_model(item)
    generate_pdf_report(item_dict, str(pdf_path))

    return FileResponse(
        path=str(pdf_path),
        filename=pdf_filename,
        media_type="application/pdf"
    )

@app.get("/api/reports/list")
def list_reports(db: Session = Depends(get_db)):
    items = db.query(MaterialInspection).order_by(desc(MaterialInspection.created_at)).limit(50).all()
    return [
        {
            "id": it.id,
            "material_category": it.material_category,
            "condition": it.condition,
            "recommendation": it.recommendation,
            "created_at": it.created_at,
            "inspector_name": it.inspector_name,
            "pdf_url": f"/api/reports/{it.id}/pdf"
        }
        for it in items
    ]


# ------------------ AI MODEL EVALUATION MODULE ------------------

@app.get("/api/ai/evaluation", response_model=ModelEvaluationResponse)
def get_ai_evaluation():
    data = get_model_evaluation()
    return {
        "overall_metrics": data["overall"],
        "class_metrics": data["classes"],
        "confusion_matrix": data["confusion_matrix"],
        "defect_detection_metrics": data["defect_detection_metrics"],
        "hardware_info": data["hardware_info"],
        "disclaimer": data["disclaimer"]
    }

# ------------------ HEALTH CHECK ------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Construction AI Quality & Reusability Assessment",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# ------------------ SPA STATIC FILES SERVING ------------------
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept API or Uploads routes
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")

