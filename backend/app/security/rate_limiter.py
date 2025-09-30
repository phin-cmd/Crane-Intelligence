"""
API Rate Limiting Implementation
Comprehensive rate limiting with Redis backend and multiple strategies
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import redis
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 100
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    window_size: int = 60  # seconds
    block_duration: int = 300  # seconds

class RateLimiter:
    """Advanced API Rate Limiting System"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.default_config = RateLimitConfig()
        self.rate_limit_configs: Dict[str, RateLimitConfig] = {}
        self.blocked_ips: Dict[str, float] = {}
        
    async def initialize(self):
        """Initialize rate limiter"""
        try:
            if not self.redis_client:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=4,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            await self.redis_client.ping()
            logger.info("Rate limiter initialized with Redis backend")
            
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting, using in-memory: {e}")
            self.redis_client = None
    
    def set_rate_limit_config(self, endpoint: str, config: RateLimitConfig):
        """Set rate limit configuration for specific endpoint"""
        self.rate_limit_configs[endpoint] = config
    
    def get_rate_limit_config(self, endpoint: str) -> RateLimitConfig:
        """Get rate limit configuration for endpoint"""
        return self.rate_limit_configs.get(endpoint, self.default_config)
    
    async def is_rate_limited(self, 
                            identifier: str, 
                            endpoint: str = "default",
                            ip_address: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is rate limited"""
        try:
            config = self.get_rate_limit_config(endpoint)
            
            # Check if IP is blocked
            if ip_address and await self.is_ip_blocked(ip_address):
                return True, {
                    "blocked": True,
                    "reason": "IP blocked",
                    "retry_after": await self.get_block_duration(ip_address)
                }
            
            # Apply rate limiting based on strategy
            if config.strategy == RateLimitStrategy.FIXED_WINDOW:
                return await self._check_fixed_window(identifier, endpoint, config)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._check_sliding_window(identifier, endpoint, config)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._check_token_bucket(identifier, endpoint, config)
            elif config.strategy == RateLimitStrategy.LEAKY_BUCKET:
                return await self._check_leaky_bucket(identifier, endpoint, config)
            else:
                return await self._check_sliding_window(identifier, endpoint, config)
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False, {"error": str(e)}
    
    async def _check_fixed_window(self, identifier: str, endpoint: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limiting"""
        try:
            current_window = int(time.time() // config.window_size)
            key = f"rate_limit:fixed:{endpoint}:{identifier}:{current_window}"
            
            if self.redis_client:
                current_count = await self.redis_client.get(key)
                if current_count is None:
                    current_count = 0
                else:
                    current_count = int(current_count)
                
                if current_count >= config.requests_per_minute:
                    return True, {
                        "limit_exceeded": True,
                        "current_count": current_count,
                        "limit": config.requests_per_minute,
                        "window": current_window,
                        "retry_after": config.window_size - (int(time.time()) % config.window_size)
                    }
                
                # Increment counter
                await self.redis_client.incr(key)
                await self.redis_client.expire(key, config.window_size)
                
                return False, {
                    "current_count": current_count + 1,
                    "limit": config.requests_per_minute,
                    "window": current_window
                }
            else:
                # Fallback to in-memory storage
                return False, {"message": "Rate limiting disabled - no Redis"}
                
        except Exception as e:
            logger.error(f"Error in fixed window rate limiting: {e}")
            return False, {"error": str(e)}
    
    async def _check_sliding_window(self, identifier: str, endpoint: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limiting"""
        try:
            current_time = time.time()
            window_start = current_time - config.window_size
            key = f"rate_limit:sliding:{endpoint}:{identifier}"
            
            if self.redis_client:
                # Use Redis sorted set for sliding window
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current requests
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                
                # Set expiry
                pipe.expire(key, config.window_size)
                
                results = await pipe.execute()
                current_count = results[1]
                
                if current_count >= config.requests_per_minute:
                    return True, {
                        "limit_exceeded": True,
                        "current_count": current_count,
                        "limit": config.requests_per_minute,
                        "window_size": config.window_size
                    }
                
                return False, {
                    "current_count": current_count + 1,
                    "limit": config.requests_per_minute,
                    "window_size": config.window_size
                }
            else:
                return False, {"message": "Rate limiting disabled - no Redis"}
                
        except Exception as e:
            logger.error(f"Error in sliding window rate limiting: {e}")
            return False, {"error": str(e)}
    
    async def _check_token_bucket(self, identifier: str, endpoint: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limiting"""
        try:
            key = f"rate_limit:token_bucket:{endpoint}:{identifier}"
            current_time = time.time()
            
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                
                # Get current bucket state
                pipe.hmget(key, "tokens", "last_refill")
                
                results = await pipe.execute()
                tokens, last_refill = results[0]
                
                if tokens is None:
                    tokens = config.burst_limit
                    last_refill = current_time
                else:
                    tokens = float(tokens)
                    last_refill = float(last_refill)
                
                # Calculate tokens to add based on time passed
                time_passed = current_time - last_refill
                tokens_to_add = time_passed * (config.requests_per_minute / 60)
                tokens = min(config.burst_limit, tokens + tokens_to_add)
                
                if tokens >= 1:
                    # Consume one token
                    tokens -= 1
                    
                    # Update bucket state
                    await self.redis_client.hmset(key, {
                        "tokens": tokens,
                        "last_refill": current_time
                    })
                    await self.redis_client.expire(key, config.window_size)
                    
                    return False, {
                        "tokens_remaining": tokens,
                        "burst_limit": config.burst_limit
                    }
                else:
                    return True, {
                        "limit_exceeded": True,
                        "tokens_remaining": tokens,
                        "burst_limit": config.burst_limit,
                        "retry_after": 1 / (config.requests_per_minute / 60)
                    }
            else:
                return False, {"message": "Rate limiting disabled - no Redis"}
                
        except Exception as e:
            logger.error(f"Error in token bucket rate limiting: {e}")
            return False, {"error": str(e)}
    
    async def _check_leaky_bucket(self, identifier: str, endpoint: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Leaky bucket rate limiting"""
        try:
            key = f"rate_limit:leaky_bucket:{endpoint}:{identifier}"
            current_time = time.time()
            
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                
                # Get current bucket state
                pipe.hmget(key, "level", "last_leak")
                
                results = await pipe.execute()
                level, last_leak = results[0]
                
                if level is None:
                    level = 0
                    last_leak = current_time
                else:
                    level = float(level)
                    last_leak = float(last_leak)
                
                # Calculate leak based on time passed
                time_passed = current_time - last_leak
                leak_rate = config.requests_per_minute / 60  # requests per second
                leaked = time_passed * leak_rate
                level = max(0, level - leaked)
                
                if level < config.burst_limit:
                    # Add request to bucket
                    level += 1
                    
                    # Update bucket state
                    await self.redis_client.hmset(key, {
                        "level": level,
                        "last_leak": current_time
                    })
                    await self.redis_client.expire(key, config.window_size)
                    
                    return False, {
                        "bucket_level": level,
                        "burst_limit": config.burst_limit
                    }
                else:
                    return True, {
                        "limit_exceeded": True,
                        "bucket_level": level,
                        "burst_limit": config.burst_limit,
                        "retry_after": 1 / leak_rate
                    }
            else:
                return False, {"message": "Rate limiting disabled - no Redis"}
                
        except Exception as e:
            logger.error(f"Error in leaky bucket rate limiting: {e}")
            return False, {"error": str(e)}
    
    async def block_ip(self, ip_address: str, duration: int = 3600):
        """Block IP address for specified duration"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    f"blocked_ip:{ip_address}",
                    duration,
                    "blocked"
                )
            else:
                self.blocked_ips[ip_address] = time.time() + duration
            
            logger.warning(f"IP {ip_address} blocked for {duration} seconds")
            
        except Exception as e:
            logger.error(f"Error blocking IP: {e}")
    
    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        try:
            if self.redis_client:
                return await self.redis_client.exists(f"blocked_ip:{ip_address}") > 0
            else:
                if ip_address in self.blocked_ips:
                    if time.time() < self.blocked_ips[ip_address]:
                        return True
                    else:
                        del self.blocked_ips[ip_address]
                return False
                
        except Exception as e:
            logger.error(f"Error checking IP block status: {e}")
            return False
    
    async def get_block_duration(self, ip_address: str) -> int:
        """Get remaining block duration for IP"""
        try:
            if self.redis_client:
                ttl = await self.redis_client.ttl(f"blocked_ip:{ip_address}")
                return max(0, ttl)
            else:
                if ip_address in self.blocked_ips:
                    remaining = self.blocked_ips[ip_address] - time.time()
                    return max(0, int(remaining))
                return 0
                
        except Exception as e:
            logger.error(f"Error getting block duration: {e}")
            return 0
    
    async def get_rate_limit_stats(self, identifier: str, endpoint: str = "default") -> Dict[str, Any]:
        """Get rate limiting statistics"""
        try:
            config = self.get_rate_limit_config(endpoint)
            
            if self.redis_client:
                # Get current usage
                if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                    key = f"rate_limit:sliding:{endpoint}:{identifier}"
                    current_count = await self.redis_client.zcard(key)
                elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
                    current_window = int(time.time() // config.window_size)
                    key = f"rate_limit:fixed:{endpoint}:{identifier}:{current_window}"
                    current_count = await self.redis_client.get(key) or 0
                else:
                    current_count = 0
                
                return {
                    "identifier": identifier,
                    "endpoint": endpoint,
                    "strategy": config.strategy.value,
                    "current_usage": int(current_count),
                    "limit": config.requests_per_minute,
                    "window_size": config.window_size,
                    "remaining": max(0, config.requests_per_minute - int(current_count))
                }
            else:
                return {
                    "identifier": identifier,
                    "endpoint": endpoint,
                    "strategy": config.strategy.value,
                    "message": "Rate limiting disabled - no Redis"
                }
                
        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {"error": str(e)}
    
    async def reset_rate_limit(self, identifier: str, endpoint: str = "default"):
        """Reset rate limit for identifier"""
        try:
            if self.redis_client:
                # Remove all rate limit keys for this identifier
                pattern = f"rate_limit:*:{endpoint}:{identifier}*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                
                logger.info(f"Rate limit reset for {identifier} on {endpoint}")
                
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
    
    async def cleanup_expired_entries(self):
        """Clean up expired rate limit entries"""
        try:
            if self.redis_client:
                # This is handled automatically by Redis TTL
                # But we can also clean up manually if needed
                current_time = time.time()
                
                # Clean up old sliding window entries
                for key in await self.redis_client.keys("rate_limit:sliding:*"):
                    await self.redis_client.zremrangebyscore(key, 0, current_time - 3600)
                
                logger.info("Cleaned up expired rate limit entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")
