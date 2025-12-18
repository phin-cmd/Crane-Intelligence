"""
Admin Core Algorithm Settings Management API
CRUD operations for core algorithm configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...models.admin import AdminUser, SystemSetting
from ...core.admin_auth import get_current_admin_user, require_super_admin

router = APIRouter(prefix="/admin/algorithm", tags=["admin-algorithm"])


class AlgorithmSettingResponse(BaseModel):
    key: str
    value: Any
    description: str
    category: str
    updated_at: Optional[datetime]


class AlgorithmSettingUpdate(BaseModel):
    value: Any


# Default algorithm settings
DEFAULT_ALGORITHM_SETTINGS = {
    "valuation": {
        "confidence_threshold": 0.7,
        "min_comparables": 3,
        "max_comparables": 10,
        "price_variance_threshold": 0.15,
        "age_weight": 0.3,
        "hours_weight": 0.25,
        "condition_weight": 0.25,
        "location_weight": 0.2
    },
    "market_data": {
        "refresh_interval_hours": 24,
        "data_retention_days": 365,
        "trend_calculation_days": 30,
        "price_index_base_year": 2020
    },
    "scoring": {
        "deal_score_weights": {
            "price": 0.4,
            "condition": 0.3,
            "market_position": 0.2,
            "maintenance": 0.1
        },
        "wear_score_thresholds": {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        }
    },
    "api": {
        "rate_limit_per_minute": 60,
        "max_concurrent_requests": 10,
        "timeout_seconds": 30
    }
}


@router.get("", response_model=Dict[str, Any])
async def get_algorithm_settings(
    category: Optional[str] = None,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get all algorithm settings or filter by category"""
    settings = {}
    
    # Get settings from database
    query = db.query(SystemSetting).filter(SystemSetting.key.like("algorithm.%"))
    if category:
        query = query.filter(SystemSetting.key.like(f"algorithm.{category}.%"))
    
    db_settings = query.all()
    
    # Build settings dict from database
    for setting in db_settings:
        key_parts = setting.key.split(".")
        if len(key_parts) >= 3:
            category_name = key_parts[1]
            setting_name = ".".join(key_parts[2:])
            
            if category_name not in settings:
                settings[category_name] = {}
            settings[category_name][setting_name] = setting.value
    
    # Merge with defaults for missing values
    if not category:
        for cat, defaults in DEFAULT_ALGORITHM_SETTINGS.items():
            if cat not in settings:
                settings[cat] = defaults
            else:
                for key, value in defaults.items():
                    if key not in settings[cat]:
                        settings[cat][key] = value
    else:
        if category in DEFAULT_ALGORITHM_SETTINGS:
            defaults = DEFAULT_ALGORITHM_SETTINGS[category]
            if category not in settings:
                settings[category] = defaults
            else:
                for key, value in defaults.items():
                    if key not in settings[category]:
                        settings[category][key] = value
    
    return settings


@router.get("/{category}/{setting_key}")
async def get_algorithm_setting(
    category: str,
    setting_key: str,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific algorithm setting"""
    full_key = f"algorithm.{category}.{setting_key}"
    setting = db.query(SystemSetting).filter(SystemSetting.key == full_key).first()
    
    if not setting:
        # Return default if exists
        if category in DEFAULT_ALGORITHM_SETTINGS:
            if setting_key in DEFAULT_ALGORITHM_SETTINGS[category]:
                return {
                    "key": full_key,
                    "value": DEFAULT_ALGORITHM_SETTINGS[category][setting_key],
                    "category": category,
                    "is_default": True
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting not found: {category}.{setting_key}"
        )
    
    return {
        "key": setting.key,
        "value": setting.value,
        "category": category,
        "updated_at": setting.updated_at,
        "is_default": False
    }


@router.put("/{category}/{setting_key}")
async def update_algorithm_setting(
    category: str,
    setting_key: str,
    setting_data: AlgorithmSettingUpdate,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Update a specific algorithm setting"""
    full_key = f"algorithm.{category}.{setting_key}"
    setting = db.query(SystemSetting).filter(SystemSetting.key == full_key).first()
    
    if not setting:
        # Create new setting
        setting = SystemSetting(
            key=full_key,
            value=setting_data.value,
            description=f"Algorithm setting: {category}.{setting_key}",
            category="algorithm"
        )
        db.add(setting)
    else:
        setting.value = setting_data.value
        setting.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(setting)
    
    return {
        "key": setting.key,
        "value": setting.value,
        "category": category,
        "updated_at": setting.updated_at,
        "message": "Setting updated successfully"
    }


@router.post("/{category}/{setting_key}/reset")
async def reset_algorithm_setting(
    category: str,
    setting_key: str,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Reset a setting to its default value"""
    full_key = f"algorithm.{category}.{setting_key}"
    setting = db.query(SystemSetting).filter(SystemSetting.key == full_key).first()
    
    # Get default value
    if category not in DEFAULT_ALGORITHM_SETTINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default value for {category}.{setting_key}"
        )
    
    if setting_key not in DEFAULT_ALGORITHM_SETTINGS[category]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default value for {category}.{setting_key}"
        )
    
    default_value = DEFAULT_ALGORITHM_SETTINGS[category][setting_key]
    
    if setting:
        setting.value = default_value
        setting.updated_at = datetime.utcnow()
    else:
        setting = SystemSetting(
            key=full_key,
            value=default_value,
            description=f"Algorithm setting: {category}.{setting_key}",
            category="algorithm"
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    
    return {
        "key": setting.key,
        "value": setting.value,
        "category": category,
        "updated_at": setting.updated_at,
        "message": "Setting reset to default"
    }


@router.get("/stats/summary")
async def get_algorithm_stats(
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get algorithm performance statistics"""
    # This would typically query usage logs and performance metrics
    # For now, return placeholder data
    return {
        "total_valuations": 0,
        "average_confidence": 0.0,
        "average_processing_time_ms": 0,
        "error_rate": 0.0,
        "settings_modified": db.query(SystemSetting).filter(
            SystemSetting.key.like("algorithm.%")
        ).count()
    }

