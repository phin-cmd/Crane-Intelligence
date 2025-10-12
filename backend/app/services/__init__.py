"""
Crane Intelligence Platform - Services Module
Provides core business logic services for valuation, rental rates, and market analysis
"""

from .smart_rental_engine import calculate_smart_rental_rates, SmartRentalEngine
from .comprehensive_valuation_engine import comprehensive_valuation_engine
from .valuation_engine import CraneValuationEngine, CraneSpecs, ValuationResult
from .auth_service import auth_service, subscription_service, get_current_user
from .specs_catalog_service import SpecsCatalogService
from .data_migration_service import data_migration_service

__all__ = [
    'calculate_smart_rental_rates',
    'SmartRentalEngine',
    'comprehensive_valuation_engine',
    'CraneValuationEngine',
    'CraneSpecs',
    'ValuationResult',
    'auth_service',
    'subscription_service',
    'get_current_user',
    'SpecsCatalogService',
    'data_migration_service'
]

