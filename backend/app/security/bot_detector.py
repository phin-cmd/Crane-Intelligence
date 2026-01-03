"""
Bot Detection System
Detects and blocks bots, crawlers, and AI agents
"""

import logging
from typing import Dict, Any, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class BotDetector:
    """Detect and block bots, crawlers, and AI agents"""
    
    BOT_USER_AGENTS = [
        "bot", "crawler", "spider", "scraper", "curl", "wget",
        "python-requests", "go-http-client", "java", "scrapy",
        "chatgpt", "gpt", "claude", "anthropic", "openai",
        "googlebot", "bingbot", "slurp", "duckduckbot", "baiduspider",
        "yandexbot", "sogou", "exabot", "facebot", "ia_archiver",
        "ahrefsbot", "semrushbot", "dotbot", "mj12bot", "rogerbot"
    ]
    
    SUSPICIOUS_PATTERNS = [
        r"^$",  # Empty user agent
        r"^[A-Z]{2,}$",  # All caps (suspicious)
        r"^[a-z]{2,}$",  # All lowercase (suspicious)
    ]
    
    @staticmethod
    def is_bot(user_agent: str) -> bool:
        """Detect if request is from a bot"""
        if not user_agent:
            return True  # No user agent = likely bot
        
        user_agent_lower = user_agent.lower()
        return any(bot in user_agent_lower for bot in BotDetector.BOT_USER_AGENTS)
    
    @staticmethod
    async def check_bot_behavior(
        ip: str,
        request_path: str,
        headers: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Check for bot-like behavior
        Returns: (is_bot, reason)
        """
        # Check user agent
        user_agent = headers.get("user-agent", "")
        if BotDetector.is_bot(user_agent):
            return True, f"Bot user agent detected: {user_agent}"
        
        # Check for missing common headers
        if not headers.get("accept-language"):
            return True, "Missing Accept-Language header"
        
        if not headers.get("accept"):
            return True, "Missing Accept header"
        
        # Check for suspicious patterns
        for pattern in BotDetector.SUSPICIOUS_PATTERNS:
            if re.match(pattern, user_agent):
                return True, f"Suspicious user agent pattern: {pattern}"
        
        # Check for API endpoints being accessed by bots
        if request_path.startswith("/api/") and not headers.get("authorization"):
            # Some bots might try to access API without auth
            if BotDetector.is_bot(user_agent):
                return True, "Bot attempting to access API without authorization"
        
        return False, ""

