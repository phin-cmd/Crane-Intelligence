"""
XSS (Cross-Site Scripting) Protection
Comprehensive XSS detection and prevention system
"""

import re
import html
import logging
import bleach
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs
import hashlib

logger = logging.getLogger(__name__)

class XSSDetector:
    """Advanced XSS Detection System"""
    
    def __init__(self):
        # XSS attack patterns
        self.xss_patterns = [
            # Script tag injection
            r'<script[^>]*>.*?</script>',
            r'<script[^>]*>',
            r'</script>',
            
            # Event handler injection
            r'on\w+\s*=\s*["\'][^"\']*["\']',
            r'on\w+\s*=\s*[^>\s]+',
            
            # JavaScript protocol
            r'javascript\s*:',
            r'vbscript\s*:',
            r'data\s*:',
            
            # Iframe injection
            r'<iframe[^>]*>.*?</iframe>',
            r'<iframe[^>]*>',
            
            # Object/Embed injection
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>',
            r'<applet[^>]*>.*?</applet>',
            
            # Form injection
            r'<form[^>]*>.*?</form>',
            r'<input[^>]*>',
            
            # Style injection
            r'<style[^>]*>.*?</style>',
            r'style\s*=\s*["\'][^"\']*["\']',
            
            # Expression injection (CSS)
            r'expression\s*\(',
            r'@import',
            
            # SVG injection
            r'<svg[^>]*>.*?</svg>',
            r'<svg[^>]*>',
            
            # Meta refresh injection
            r'<meta[^>]*http-equiv\s*=\s*["\']refresh["\'][^>]*>',
            
            # Link injection
            r'<link[^>]*>',
            
            # Base tag injection
            r'<base[^>]*>',
            
            # Advanced XSS patterns
            r'<img[^>]*src\s*=\s*["\']javascript:',
            r'<img[^>]*onerror\s*=',
            r'<img[^>]*onload\s*=',
            
            # DOM-based XSS
            r'document\.',
            r'window\.',
            r'location\.',
            r'history\.',
            
            # Cookie manipulation
            r'document\.cookie',
            r'document\.domain',
            
            # Local storage manipulation
            r'localStorage\.',
            r'sessionStorage\.',
            
            # AJAX requests
            r'XMLHttpRequest',
            r'fetch\s*\(',
            r'\.ajax\s*\(',
            
            # Eval and Function
            r'eval\s*\(',
            r'Function\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            
            # String manipulation for XSS
            r'String\.fromCharCode',
            r'unescape\s*\(',
            r'decodeURIComponent\s*\(',
            
            # Event listener injection
            r'addEventListener\s*\(',
            r'attachEvent\s*\(',
            
            # InnerHTML manipulation
            r'\.innerHTML\s*=',
            r'\.outerHTML\s*=',
            r'\.insertAdjacentHTML\s*\(',
            
            # Document manipulation
            r'document\.write\s*\(',
            r'document\.writeln\s*\(',
            
            # URL manipulation
            r'location\.href\s*=',
            r'location\.replace\s*\(',
            r'location\.assign\s*\(',
            
            # Form manipulation
            r'\.submit\s*\(',
            r'\.reset\s*\(',
            
            # Advanced evasion techniques
            r'&#x?[0-9a-fA-F]+;',
            r'%[0-9a-fA-F]{2}',
            r'\\x[0-9a-fA-F]{2}',
            r'\\u[0-9a-fA-F]{4}',
            
            # Case variation patterns
            r'<ScRiPt',
            r'<SCRIPT',
            r'<script',
            r'JaVaScRiPt',
            r'JAVASCRIPT',
            r'javascript',
            
            # Mixed case event handlers
            r'OnLoAd',
            r'ONLOAD',
            r'onload',
            r'OnClIcK',
            r'ONCLICK',
            r'onclick',
            
            # Encoded patterns
            r'%3Cscript',
            r'%3C/script',
            r'&lt;script',
            r'&lt;/script',
            
            # Null byte injection
            r'%00',
            r'\x00',
            r'\0',
            
            # Unicode injection
            r'\u003c',
            r'\u003e',
            r'\u0027',
            r'\u0022',
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.xss_patterns]
        
        # Safe HTML tags
        self.safe_tags = {
            'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'span', 'div',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
            'blockquote', 'code', 'pre', 'a', 'img'
        }
        
        # Safe HTML attributes
        self.safe_attributes = {
            'href', 'src', 'alt', 'title', 'class', 'id', 'style',
            'width', 'height', 'align', 'valign', 'colspan', 'rowspan'
        }
        
        # Dangerous HTML attributes
        self.dangerous_attributes = {
            'onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout',
            'onfocus', 'onblur', 'onchange', 'onsubmit', 'onreset',
            'onkeydown', 'onkeyup', 'onkeypress', 'onmousedown',
            'onmouseup', 'onmousemove', 'onmouseenter', 'onmouseleave',
            'ondblclick', 'oncontextmenu', 'onwheel', 'ontouchstart',
            'ontouchend', 'ontouchmove', 'ontouchcancel'
        }
    
    def detect_xss(self, content: str) -> Tuple[bool, List[str]]:
        """Detect potential XSS attacks in content"""
        if not content:
            return False, []
        
        threats = []
        
        # Check for XSS patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(content)
            if matches:
                threats.extend([f"XSS pattern detected: {match}" for match in matches])
        
        # Check for dangerous attributes
        for attr in self.dangerous_attributes:
            if attr in content.lower():
                threats.append(f"Dangerous attribute detected: {attr}")
        
        # Check for script injection in URLs
        if 'javascript:' in content.lower():
            threats.append("JavaScript protocol detected in URL")
        
        # Check for data URI with script
        if 'data:text/html' in content.lower():
            threats.append("Data URI with HTML content detected")
        
        # Check for encoded XSS
        if any(encoded in content.lower() for encoded in ['%3cscript', '&lt;script', '&#60;script']):
            threats.append("Encoded script tag detected")
        
        return len(threats) > 0, threats
    
    def sanitize_html(self, content: str, allowed_tags: Optional[List[str]] = None,
                     allowed_attributes: Optional[List[str]] = None,
                     strip_html: bool = False) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not content:
            return ""
        
        # Use provided tags or safe defaults
        tags = allowed_tags or list(self.safe_tags)
        attributes = allowed_attributes or list(self.safe_attributes)
        
        if strip_html:
            # Remove all HTML tags
            return bleach.clean(content, tags=[], attributes={}, strip=True)
        else:
            # Clean HTML with allowed tags and attributes
            return bleach.clean(
                content,
                tags=tags,
                attributes=attributes,
                strip=True,
                protocols=['http', 'https', 'mailto']
            )
    
    def escape_html(self, content: str) -> str:
        """Escape HTML entities to prevent XSS"""
        if not content:
            return ""
        
        return html.escape(content, quote=True)
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL for XSS prevention"""
        if not url:
            return False, "Empty URL"
        
        try:
            parsed = urlparse(url)
            
            # Check protocol
            if parsed.scheme not in ['http', 'https', 'mailto']:
                return False, f"Dangerous protocol: {parsed.scheme}"
            
            # Check for JavaScript protocol
            if 'javascript:' in url.lower():
                return False, "JavaScript protocol not allowed"
            
            # Check for data URI with dangerous content
            if parsed.scheme == 'data':
                if 'text/html' in url.lower() or 'script' in url.lower():
                    return False, "Data URI with HTML/script content not allowed"
            
            return True, "URL is safe"
            
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    def sanitize_json(self, json_content: str) -> str:
        """Sanitize JSON content to prevent XSS"""
        if not json_content:
            return ""
        
        try:
            # Parse JSON
            data = json.loads(json_content)
            
            # Recursively sanitize string values
            sanitized_data = self._sanitize_json_recursive(data)
            
            return json.dumps(sanitized_data)
            
        except json.JSONDecodeError:
            # If not valid JSON, treat as string and escape
            return self.escape_html(json_content)
    
    def _sanitize_json_recursive(self, obj: Any) -> Any:
        """Recursively sanitize JSON object"""
        if isinstance(obj, dict):
            return {key: self._sanitize_json_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_json_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return self.escape_html(obj)
        else:
            return obj
    
    def get_xss_security_report(self, content: str) -> Dict[str, Any]:
        """Get comprehensive XSS security report"""
        try:
            # Detect XSS
            is_xss, threats = self.detect_xss(content)
            
            # Count dangerous patterns
            dangerous_pattern_count = 0
            for pattern in self.compiled_patterns:
                matches = pattern.findall(content)
                dangerous_pattern_count += len(matches)
            
            # Count dangerous attributes
            dangerous_attr_count = 0
            for attr in self.dangerous_attributes:
                if attr in content.lower():
                    dangerous_attr_count += 1
            
            # Calculate risk score
            risk_score = 0
            if is_xss:
                risk_score += 50
            risk_score += dangerous_pattern_count * 10
            risk_score += dangerous_attr_count * 15
            
            # Check for encoding attempts
            encoding_attempts = 0
            if any(encoded in content.lower() for encoded in ['%3c', '&lt;', '&#60;', '\\x3c', '\\u003c']):
                encoding_attempts += 1
            
            return {
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                "is_safe": not is_xss,
                "risk_score": min(100, risk_score),
                "xss_detected": is_xss,
                "threats": threats,
                "dangerous_patterns": dangerous_pattern_count,
                "dangerous_attributes": dangerous_attr_count,
                "encoding_attempts": encoding_attempts,
                "content_length": len(content),
                "recommendations": self._get_xss_recommendations(is_xss, dangerous_pattern_count, dangerous_attr_count)
            }
            
        except Exception as e:
            logger.error(f"Error generating XSS security report: {e}")
            return {"error": str(e)}
    
    def _get_xss_recommendations(self, is_xss: bool, dangerous_patterns: int, 
                               dangerous_attributes: int) -> List[str]:
        """Get XSS prevention recommendations"""
        recommendations = []
        
        if is_xss:
            recommendations.append("Content contains XSS patterns - sanitize immediately")
            recommendations.append("Use HTML sanitization library like Bleach")
            recommendations.append("Implement Content Security Policy (CSP)")
        
        if dangerous_patterns > 0:
            recommendations.append("Remove or escape dangerous HTML patterns")
            recommendations.append("Use whitelist approach for HTML content")
        
        if dangerous_attributes > 0:
            recommendations.append("Remove dangerous HTML attributes")
            recommendations.append("Use safe HTML attribute whitelist")
        
        if not recommendations:
            recommendations.append("Content appears to be safe from XSS")
        
        return recommendations

class XSSProtection:
    """XSS Protection System"""
    
    def __init__(self):
        self.detector = XSSDetector()
        self.blocked_content = set()
        self.content_cache = {}
    
    def protect_input(self, content: str, content_type: str = "text") -> str:
        """Protect input content from XSS"""
        if not content:
            return ""
        
        # Check if content is blocked
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        if content_hash in self.blocked_content:
            raise ValueError("Content is blocked due to XSS concerns")
        
        # Detect XSS
        is_xss, threats = self.detector.detect_xss(content)
        if is_xss:
            logger.warning(f"XSS attempt blocked: {threats}")
            self.blocked_content.add(content_hash)
            raise ValueError(f"XSS attempt blocked: {', '.join(threats)}")
        
        # Apply protection based on content type
        if content_type == "html":
            return self.detector.sanitize_html(content)
        elif content_type == "json":
            return self.detector.sanitize_json(content)
        elif content_type == "url":
            is_valid, message = self.detector.validate_url(content)
            if not is_valid:
                raise ValueError(f"Invalid URL: {message}")
            return content
        else:
            return self.detector.escape_html(content)
    
    def protect_output(self, content: str, output_type: str = "html") -> str:
        """Protect output content from XSS"""
        if not content:
            return ""
        
        if output_type == "html":
            return self.detector.sanitize_html(content)
        elif output_type == "json":
            return self.detector.sanitize_json(content)
        else:
            return self.detector.escape_html(content)
    
    def create_csp_header(self, allow_inline: bool = False, 
                         allow_eval: bool = False) -> str:
        """Create Content Security Policy header"""
        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'"
        ]
        
        if allow_inline:
            csp_directives[1] = "script-src 'self' 'unsafe-inline'"
        
        if allow_eval:
            csp_directives[1] += " 'unsafe-eval'"
        
        return "; ".join(csp_directives)
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """Get XSS protection statistics"""
        return {
            "blocked_content_count": len(self.blocked_content),
            "cached_content_count": len(self.content_cache),
            "detector_patterns": len(self.detector.xss_patterns),
            "safe_tags": len(self.detector.safe_tags),
            "safe_attributes": len(self.detector.safe_attributes),
            "dangerous_attributes": len(self.detector.dangerous_attributes)
        }
