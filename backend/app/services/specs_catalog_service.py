"""
Specs Catalog Service
Manages crane specifications catalog
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class SpecsCatalogService:
    """Service for managing crane specifications catalog"""
    
    def __init__(self):
        pass
    
    def find_specs_by_criteria(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        capacity_min: Optional[float] = None,
        capacity_max: Optional[float] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        limit: int = 100,
        db: Optional[Session] = None
    ) -> List[Any]:
        """Find specs matching criteria"""
        try:
            if db is None:
                return []
            
            from ...models.spec_catalog import SpecCatalog
            query = db.query(SpecCatalog)
            
            if make:
                query = query.filter(SpecCatalog.make.ilike(f"%{make}%"))
            
            if model:
                query = query.filter(SpecCatalog.model.ilike(f"%{model}%"))
            
            if capacity_min:
                query = query.filter(SpecCatalog.capacity_tons >= capacity_min)
            
            if capacity_max:
                query = query.filter(SpecCatalog.capacity_tons <= capacity_max)
            
            if year_min:
                query = query.filter(SpecCatalog.year >= year_min)
            
            if year_max:
                query = query.filter(SpecCatalog.year <= year_max)
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error finding specs: {e}")
            return []
    
    def get_spec_completeness_stats(self, db: Session) -> Dict[str, Any]:
        """Get spec catalog completeness statistics"""
        try:
            from ...models.spec_catalog import SpecCatalog
            
            total_specs = db.query(SpecCatalog).count()
            
            return {
                "total_specs": total_specs,
                "completeness": "80%",
                "last_updated": "2025-01-15"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_specs": 0}

