"""
API Configuration and Authentication Management
Centralized configuration for all external API integrations
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API configuration for external services"""
    api_key: str
    base_url: str
    rate_limit: int
    timeout: int
    retry_count: int
    cache_duration: int

class APIConfigManager:
    """Centralized API configuration manager"""
    
    def __init__(self):
        self.configs = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load API configurations from environment variables"""
        
        # Equipment Watch API Configuration
        self.configs['equipment_watch'] = APIConfig(
            api_key=os.getenv('EQUIPMENT_WATCH_API_KEY', 'demo_key_equipment_watch_2024'),
            base_url=os.getenv('EQUIPMENT_WATCH_BASE_URL', 'https://api.equipmentwatch.com/v1'),
            rate_limit=int(os.getenv('EQUIPMENT_WATCH_RATE_LIMIT', '100')),
            timeout=int(os.getenv('EQUIPMENT_WATCH_TIMEOUT', '30')),
            retry_count=int(os.getenv('EQUIPMENT_WATCH_RETRY_COUNT', '3')),
            cache_duration=int(os.getenv('EQUIPMENT_WATCH_CACHE_DURATION', '3600'))
        )
        
        # Ritchie Bros API Configuration
        self.configs['ritchie_bros'] = APIConfig(
            api_key=os.getenv('RITCHIE_BROS_API_KEY', 'demo_key_ritchie_bros_2024'),
            base_url=os.getenv('RITCHIE_BROS_BASE_URL', 'https://api.ritchiebros.com/v1'),
            rate_limit=int(os.getenv('RITCHIE_BROS_RATE_LIMIT', '50')),
            timeout=int(os.getenv('RITCHIE_BROS_TIMEOUT', '30')),
            retry_count=int(os.getenv('RITCHIE_BROS_RETRY_COUNT', '3')),
            cache_duration=int(os.getenv('RITCHIE_BROS_CACHE_DURATION', '1800'))
        )
        
        # MachineryTrader API Configuration
        self.configs['machinery_trader'] = APIConfig(
            api_key=os.getenv('MACHINERY_TRADER_API_KEY', 'demo_key_machinery_trader_2024'),
            base_url=os.getenv('MACHINERY_TRADER_BASE_URL', 'https://api.machinerytrader.com/v1'),
            rate_limit=int(os.getenv('MACHINERY_TRADER_RATE_LIMIT', '75')),
            timeout=int(os.getenv('MACHINERY_TRADER_TIMEOUT', '30')),
            retry_count=int(os.getenv('MACHINERY_TRADER_RETRY_COUNT', '3')),
            cache_duration=int(os.getenv('MACHINERY_TRADER_CACHE_DURATION', '1800'))
        )
        
        # IronPlanet API Configuration
        self.configs['ironplanet'] = APIConfig(
            api_key=os.getenv('IRONPLANET_API_KEY', 'demo_key_ironplanet_2024'),
            base_url=os.getenv('IRONPLANET_BASE_URL', 'https://api.ironplanet.com/v1'),
            rate_limit=int(os.getenv('IRONPLANET_RATE_LIMIT', '200')),
            timeout=int(os.getenv('IRONPLANET_TIMEOUT', '30')),
            retry_count=int(os.getenv('IRONPLANET_RETRY_COUNT', '3')),
            cache_duration=int(os.getenv('IRONPLANET_CACHE_DURATION', '1800'))
        )
        
        logger.info("API configurations loaded successfully")
    
    def get_config(self, service: str) -> APIConfig:
        """Get API configuration for a specific service"""
        if service not in self.configs:
            raise ValueError(f"Unknown service: {service}")
        return self.configs[service]
    
    def update_config(self, service: str, **kwargs):
        """Update API configuration for a specific service"""
        if service not in self.configs:
            raise ValueError(f"Unknown service: {service}")
        
        config = self.configs[service]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                logger.info(f"Updated {service} config: {key} = {value}")
    
    def get_all_configs(self) -> Dict[str, APIConfig]:
        """Get all API configurations"""
        return self.configs.copy()
    
    def validate_configs(self) -> Dict[str, bool]:
        """Validate all API configurations"""
        validation_results = {}
        
        for service, config in self.configs.items():
            try:
                # Check if API key is not demo key
                is_demo = 'demo_key' in config.api_key
                validation_results[service] = {
                    'valid': True,
                    'is_demo': is_demo,
                    'has_api_key': bool(config.api_key),
                    'has_base_url': bool(config.base_url),
                    'rate_limit': config.rate_limit,
                    'timeout': config.timeout
                }
            except Exception as e:
                validation_results[service] = {
                    'valid': False,
                    'error': str(e)
                }
        
        return validation_results

# Global configuration manager instance
api_config_manager = APIConfigManager()

def get_api_config(service: str) -> APIConfig:
    """Get API configuration for a specific service"""
    return api_config_manager.get_config(service)

def validate_all_configs() -> Dict[str, Any]:
    """Validate all API configurations"""
    return api_config_manager.validate_configs()
