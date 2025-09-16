"""
Crane service - Core business logic for crane analysis and management
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from ..models.crane import Crane, CraneAnalysis, MarketData
from ..schemas.crane import CraneCreate, CraneUpdate, CraneAnalysis as CraneAnalysisSchema
import pandas as pd
import numpy as np
from datetime import datetime
import json

class CraneService:
    """Service class for crane operations and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_crane(self, crane_data: CraneCreate) -> Crane:
        """Create a new crane record"""
        db_crane = Crane(**crane_data.dict())
        self.db.add(db_crane)
        self.db.commit()
        self.db.refresh(db_crane)
        return db_crane
    
    def get_crane(self, crane_id: int) -> Optional[Crane]:
        """Get crane by ID"""
        return self.db.query(Crane).filter(Crane.id == crane_id).first()
    
    def get_cranes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        manufacturer: Optional[str] = None,
        capacity_min: Optional[float] = None,
        capacity_max: Optional[float] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        location: Optional[str] = None
    ) -> List[Crane]:
        """Get filtered list of cranes with pagination"""
        query = self.db.query(Crane)
        
        # Apply filters
        if manufacturer:
            query = query.filter(Crane.manufacturer.ilike(f"%{manufacturer}%"))
        if capacity_min is not None:
            query = query.filter(Crane.capacity_tons >= capacity_min)
        if capacity_max is not None:
            query = query.filter(Crane.capacity_tons <= capacity_max)
        if year_min is not None:
            query = query.filter(Crane.year >= year_min)
        if year_max is not None:
            query = query.filter(Crane.year <= year_max)
        if price_min is not None:
            query = query.filter(Crane.price >= price_min)
        if price_max is not None:
            query = query.filter(Crane.price <= price_max)
        if location:
            query = query.filter(Crane.location.ilike(f"%{location}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def update_crane(self, crane_id: int, crane_data: CraneUpdate) -> Optional[Crane]:
        """Update crane information"""
        db_crane = self.get_crane(crane_id)
        if not db_crane:
            return None
        
        update_data = crane_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_crane, field, value)
        
        db_crane.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_crane)
        return db_crane
    
    def delete_crane(self, crane_id: int) -> bool:
        """Delete a crane record"""
        db_crane = self.get_crane(crane_id)
        if not db_crane:
            return False
        
        self.db.delete(db_crane)
        self.db.commit()
        return True
    
    def analyze_crane(self, crane_id: int) -> Optional[CraneAnalysisSchema]:
        """Perform comprehensive crane analysis"""
        crane = self.get_crane(crane_id)
        if not crane:
            return None
        
        # Get market statistics for analysis
        market_stats = self._get_market_statistics(crane.manufacturer)
        
        # Calculate deal score and analysis
        analysis_result = self._calculate_deal_score(crane, market_stats)
        
        # Create or update analysis record
        db_analysis = self.db.query(CraneAnalysis).filter(
            CraneAnalysis.crane_id == crane_id
        ).first()
        
        if db_analysis:
            # Update existing analysis
            for field, value in analysis_result.items():
                if field != 'crane_id':
                    setattr(db_analysis, field, value)
            db_analysis.analysis_date = datetime.utcnow()
        else:
            # Create new analysis
            db_analysis = CraneAnalysis(
                crane_id=crane_id,
                **analysis_result
            )
            self.db.add(db_analysis)
        
        self.db.commit()
        self.db.refresh(db_analysis)
        
        return CraneAnalysisSchema.from_orm(db_analysis)
    
    def _calculate_deal_score(self, crane: Crane, market_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate deal score and analysis metrics"""
        current_year = datetime.now().year
        age = current_year - crane.year
        
        # Base score calculation
        base_score = 50
        
        # Age factor (0-20 points)
        if age <= 2:
            age_factor = 20
        elif age <= 5:
            age_factor = 15
        elif age <= 10:
            age_factor = 10
        elif age <= 15:
            age_factor = 5
        else:
            age_factor = 0
        
        # Hours factor (0-15 points)
        if crane.hours <= 2000:
            hours_factor = 15
        elif crane.hours <= 5000:
            hours_factor = 12
        elif crane.hours <= 10000:
            hours_factor = 8
        elif crane.hours <= 15000:
            hours_factor = 4
        else:
            hours_factor = 0
        
        # Market positioning factor (0-15 points)
        market_position = self._determine_market_position(crane, market_stats)
        market_factor = 15 if market_position == "Excellent" else 10 if market_position == "Good" else 5
        
        # Calculate final score
        deal_score = min(100, base_score + age_factor + hours_factor + market_factor)
        
        # Estimate market value
        estimated_value = self._estimate_market_value(crane, market_stats)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(crane, market_stats)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(crane, age, crane.hours)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(deal_score, risk_factors)
        
        return {
            'crane_id': crane.id,
            'deal_score': deal_score,
            'estimated_value': estimated_value,
            'confidence_score': confidence_score,
            'comparable_count': market_stats.get('comparable_count', 5),
            'market_position': market_position,
            'risk_factors': json.dumps(risk_factors),
            'recommendations': json.dumps(recommendations)
        }
    
    def _get_market_statistics(self, manufacturer: str) -> Dict[str, Any]:
        """Get market statistics for analysis"""
        # Query for manufacturer-specific stats
        manufacturer_cranes = self.db.query(Crane).filter(
            Crane.manufacturer == manufacturer
        ).all()
        
        if not manufacturer_cranes:
            # Fallback to overall market stats
            manufacturer_cranes = self.db.query(Crane).all()
        
        if not manufacturer_cranes:
            return {
                'comparable_count': 0,
                'average_price': 0,
                'price_range': {'min': 0, 'max': 0},
                'capacity_distribution': {}
            }
        
        prices = [float(crane.price) for crane in manufacturer_cranes]
        capacities = [float(crane.capacity_tons) for crane in manufacturer_cranes]
        
        return {
            'comparable_count': len(manufacturer_cranes),
            'average_price': np.mean(prices),
            'price_range': {'min': min(prices), 'max': max(prices)},
            'capacity_distribution': self._calculate_capacity_distribution(capacities)
        }
    
    def _determine_market_position(self, crane: Crane, market_stats: Dict[str, Any]) -> str:
        """Determine market positioning based on price and specifications"""
        avg_price = market_stats.get('average_price', 0)
        if avg_price == 0:
            return "Good"
        
        price_ratio = float(crane.price) / avg_price
        
        if price_ratio < 0.8:
            return "Excellent"
        elif price_ratio < 1.1:
            return "Good"
        else:
            return "Fair"
    
    def _estimate_market_value(self, crane: Crane, market_stats: Dict[str, Any]) -> float:
        """Estimate market value based on comparable sales"""
        # Simple estimation based on capacity and age
        base_value = float(crane.capacity_tons) * 10000  # Base $10k per ton
        
        # Adjust for age
        age_factor = max(0.3, 1 - (datetime.now().year - crane.year) * 0.05)
        
        # Adjust for hours
        hours_factor = max(0.5, 1 - (crane.hours / 20000) * 0.3)
        
        estimated_value = base_value * age_factor * hours_factor
        
        # Apply market adjustment
        market_adjustment = market_stats.get('average_price', estimated_value) / estimated_value
        estimated_value *= min(1.5, max(0.5, market_adjustment))
        
        return round(estimated_value, 2)
    
    def _calculate_confidence_score(self, crane: Crane, market_stats: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        comparable_count = market_stats.get('comparable_count', 0)
        
        # Base confidence on comparable count
        if comparable_count >= 20:
            base_confidence = 0.9
        elif comparable_count >= 10:
            base_confidence = 0.8
        elif comparable_count >= 5:
            base_confidence = 0.7
        else:
            base_confidence = 0.5
        
        # Adjust for data quality
        data_quality = 1.0
        if not crane.location:
            data_quality *= 0.9
        if not crane.condition:
            data_quality *= 0.9
        
        return round(base_confidence * data_quality, 2)
    
    def _identify_risk_factors(self, crane: Crane, age: int, hours: int) -> List[str]:
        """Identify potential risk factors"""
        risk_factors = []
        
        if age > 15:
            risk_factors.append("High equipment age")
        if hours > 15000:
            risk_factors.append("High operating hours")
        if age > 10 and hours > 10000:
            risk_factors.append("Combined age and hours risk")
        
        return risk_factors
    
    def _generate_recommendations(self, deal_score: int, risk_factors: List[str]) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []
        
        if deal_score >= 80:
            recommendations.append("Strong buy recommendation")
        elif deal_score >= 60:
            recommendations.append("Good investment opportunity")
        elif deal_score >= 40:
            recommendations.append("Consider with caution")
        else:
            recommendations.append("Not recommended")
        
        if risk_factors:
            recommendations.append(f"Address risk factors: {', '.join(risk_factors)}")
        
        return recommendations
    
    def _calculate_capacity_distribution(self, capacities: List[float]) -> Dict[str, int]:
        """Calculate capacity distribution for market analysis"""
        if not capacities:
            return {}
        
        capacity_ranges = {
            '0-50': 0,
            '51-100': 0,
            '101-200': 0,
            '201-300': 0,
            '301-400': 0,
            '400+': 0
        }
        
        for capacity in capacities:
            if capacity <= 50:
                capacity_ranges['0-50'] += 1
            elif capacity <= 100:
                capacity_ranges['51-100'] += 1
            elif capacity <= 200:
                capacity_ranges['101-200'] += 1
            elif capacity <= 300:
                capacity_ranges['201-300'] += 1
            elif capacity <= 400:
                capacity_ranges['301-400'] += 1
            else:
                capacity_ranges['400+'] += 1
        
        return capacity_ranges
