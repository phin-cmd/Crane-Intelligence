"""
Admin Cranes Management API
CRUD operations for crane data management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...core.database import get_db
from ...models.crane import Crane, CraneAnalysis, MarketData
from ...core.admin_auth import get_current_admin_user, require_admin_or_super_admin
from ...models.admin import AdminUser

router = APIRouter(prefix="/admin/cranes", tags=["admin-cranes"])


class CraneCreate(BaseModel):
    manufacturer: str
    model: str
    year: int
    capacity_tons: float
    hours: int
    price: float
    location: Optional[str] = None
    condition: Optional[str] = None
    description: Optional[str] = None


class CraneUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity_tons: Optional[float] = None
    hours: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    condition: Optional[str] = None
    description: Optional[str] = None


class CraneResponse(BaseModel):
    id: int
    manufacturer: str
    model: str
    year: int
    capacity_tons: float
    hours: int
    price: float
    location: Optional[str]
    condition: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("", response_model=List[CraneResponse])
async def list_cranes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    min_capacity: Optional[float] = None,
    max_capacity: Optional[float] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """List all cranes with optional filters"""
    query = db.query(Crane)
    
    if manufacturer:
        query = query.filter(Crane.manufacturer.ilike(f"%{manufacturer}%"))
    if model:
        query = query.filter(Crane.model.ilike(f"%{model}%"))
    if min_capacity:
        query = query.filter(Crane.capacity_tons >= min_capacity)
    if max_capacity:
        query = query.filter(Crane.capacity_tons <= max_capacity)
    if min_year:
        query = query.filter(Crane.year >= min_year)
    if max_year:
        query = query.filter(Crane.year <= max_year)
    
    cranes = query.offset(skip).limit(limit).all()
    return cranes


@router.get("/{crane_id}", response_model=CraneResponse)
async def get_crane(
    crane_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific crane by ID"""
    crane = db.query(Crane).filter(Crane.id == crane_id).first()
    if not crane:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crane not found"
        )
    return crane


@router.post("", response_model=CraneResponse)
async def create_crane(
    crane_data: CraneCreate,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new crane"""
    crane = Crane(
        manufacturer=crane_data.manufacturer,
        model=crane_data.model,
        year=crane_data.year,
        capacity_tons=crane_data.capacity_tons,
        hours=crane_data.hours,
        price=crane_data.price,
        location=crane_data.location,
        condition=crane_data.condition,
        description=crane_data.description
    )
    
    db.add(crane)
    db.commit()
    db.refresh(crane)
    
    return crane


@router.put("/{crane_id}", response_model=CraneResponse)
async def update_crane(
    crane_id: int,
    crane_data: CraneUpdate,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Update a crane"""
    crane = db.query(Crane).filter(Crane.id == crane_id).first()
    if not crane:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crane not found"
        )
    
    update_data = crane_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crane, field, value)
    
    crane.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(crane)
    
    return crane


@router.delete("/{crane_id}")
async def delete_crane(
    crane_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Delete a crane"""
    crane = db.query(Crane).filter(Crane.id == crane_id).first()
    if not crane:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crane not found"
        )
    
    db.delete(crane)
    db.commit()
    
    return {"message": "Crane deleted successfully"}


@router.get("/{crane_id}/analyses", response_model=List[dict])
async def get_crane_analyses(
    crane_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get all analyses for a specific crane"""
    crane = db.query(Crane).filter(Crane.id == crane_id).first()
    if not crane:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crane not found"
        )
    
    analyses = db.query(CraneAnalysis).filter(CraneAnalysis.crane_id == crane_id).all()
    return [
        {
            "id": a.id,
            "deal_score": a.deal_score,
            "estimated_value": float(a.estimated_value),
            "confidence_score": float(a.confidence_score),
            "comparable_count": a.comparable_count,
            "market_position": a.market_position,
            "analysis_date": a.analysis_date
        }
        for a in analyses
    ]

