import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), default="inspector", nullable=False)  # admin, site_engineer, inspector
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inspections = relationship("MaterialInspection", back_populates="inspector")

class MaterialInspection(Base):
    __tablename__ = "material_inspections"

    id = Column(String(50), primary_key=True, index=True)  # MAT-YYYYMMDD-XXXX
    original_image_path = Column(String(255), nullable=False)
    annotated_image_path = Column(String(255), nullable=True)
    material_category = Column(String(80), nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0 to 100
    condition = Column(String(40), nullable=False, index=True)  # GOOD, DAMAGED, INSPECTION REQUIRED
    condition_score = Column(Float, nullable=False)  # 0 to 100
    recommendation = Column(String(40), nullable=False, index=True)  # REUSE, INSPECT, REPAIR, RECYCLE, REJECT
    recommendation_reason = Column(Text, nullable=False)
    suggested_next_step = Column(Text, nullable=False)
    defects_json = Column(Text, nullable=False, default="[]")  # JSON encoded list of defect objects
    defect_count = Column(Integer, default=0)
    
    quantity = Column(Float, default=1.0)
    unit = Column(String(30), default="pieces")  # pieces, kg, tons, sq.m, cu.m, meters, bags
    site_location = Column(String(150), default="Central Yard A", index=True)
    project_name = Column(String(150), default="EcoBuild Site 1")
    inspection_status = Column(String(40), default="Verified")  # Verified, Pending, Archived
    
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspector_name = Column(String(100), default="Site Inspector")
    inspector = relationship("User", back_populates="inspections")
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=True)
    user_name = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
