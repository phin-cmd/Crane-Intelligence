"""
Brevo (formerly Sendinblue) Email Service
Uses Brevo Transactional Email API for sending emails
Enhanced with batch sending, tracking, tags, and retry logic
"""

import requests
import logging
import time
import base64
from typing import List, Optional, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)


class BrevoEmailService:
    """
    Brevo API email service
    Uses Brevo Transactional Email API v3
    """
    
    def __init__(self):
        # Read API key directly from environment or settings to ensure we get the latest value
        import os
        self.api_key = os.getenv("BREVO_API_KEY") or settings.brevo_api_key
        self.api_url = "https://api.brevo.com/v3"
        self.from_email = settings.mail_from_email
        self.from_name = settings.mail_from_name
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self._sender_verified = None  # Cache for sender verification status
        
        if not self.api_key:
            logger.warning("Brevo API key not configured. Email sending will fail.")
            logger.warning(f"Checked: os.getenv('BREVO_API_KEY')={bool(os.getenv('BREVO_API_KEY'))}, settings.brevo_api_key={bool(settings.brevo_api_key)}")
        
        # Check sender verification status
        self._check_sender_verification()
        
        # Setup Jinja2 environment for email templates
        template_dir = Path(settings.email_templates_dir)
        if not template_dir.exists():
            # Try alternative paths
            alt_paths = [
                Path(__file__).parent.parent.parent / "templates" / "emails",
                Path("/root/crane/backend/templates/emails"),
                Path("/app/templates/emails"),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    template_dir = alt_path
                    logger.info(f"Using alternative template path: {template_dir}")
                    break
            else:
                # Create default if none exist
                template_dir.mkdir(parents=True, exist_ok=True)
                logger.warning(f"Created template directory at: {template_dir}")
        
        logger.info(f"Email templates directory: {template_dir}")
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def _check_sender_verification(self) -> bool:
        """Check if sender email is verified in Brevo"""
        if not self.api_key:
            self._sender_verified = False
            return False
        
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.api_url}/senders",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                senders = response.json().get("senders", [])
                for sender in senders:
                    if sender.get("email") == self.from_email:
                        verified = sender.get("verified", False)
                        active = sender.get("active", False)
                        
                        # If sender is active, consider it verified (API may not always show verified=true)
                        # Dashboard shows verified status more accurately than API
                        if active:
                            self._sender_verified = True
                            logger.info(f"✓ Sender email is active and ready: {self.from_email}")
                            return True
                        elif verified:
                            self._sender_verified = True
                            logger.info(f"✓ Sender email verified: {self.from_email}")
                            return True
                        else:
                            self._sender_verified = False
                            logger.warning(
                                f"⚠️ SENDER EMAIL STATUS: {self.from_email}\n"
                                f"   Verified: {verified}, Active: {active}\n"
                                f"   Note: Check Brevo Dashboard for actual verification status."
                            )
                            return False
                
                # Sender not found in list
                logger.warning(
                    f"⚠️ SENDER EMAIL NOT FOUND IN BREVO: {self.from_email}\n"
                    f"   You need to add this sender in Brevo Dashboard first."
                )
                self._sender_verified = False
                return False
            else:
                logger.warning(f"Could not check sender verification: {response.status_code}")
                self._sender_verified = None  # Unknown status
                return False
        except Exception as e:
            logger.warning(f"Error checking sender verification: {e}")
            self._sender_verified = None  # Unknown status
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        try:
            logger.info(f"Rendering email template: {template_name}")
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(**context)
            logger.info(f"✓ Template {template_name} rendered successfully ({len(rendered)} chars)")
            return rendered
        except Exception as e:
            logger.error(f"✗ Failed to render template {template_name}: {e}", exc_info=True)
            import traceback
            logger.error(f"Template rendering traceback: {traceback.format_exc()}")
            # Return fallback template
            fallback_html = f"""
            <html>
            <body>
                <h2>{context.get('subject', 'Notification from Crane Intelligence')}</h2>
                <p>{context.get('message', 'You have a new notification.')}</p>
                <p>Best regards,<br>Crane Intelligence Team</p>
            </body>
            </html>
            """
            logger.warning(f"Using fallback template for {template_name}")
            return fallback_html
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        template_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send email using Brevo API with enhanced features
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            attachments: List of attachment dicts with 'name' and 'content' (base64) or 'file_path'
            reply_to: Reply-to email address (optional)
            tags: List of tags for email categorization (optional)
            params: Dictionary of parameters for template variables (optional)
            headers: Custom headers (optional)
            template_id: Brevo template ID if using Brevo templates (optional)
        
        Returns:
            Dict with 'success' (bool), 'message' (str), and 'message_id' (str)
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "Brevo API key not configured"
            }
        
        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Prepare recipients
                recipients = [{"email": email} for email in to_emails]
                
                # Prepare payload with improved headers for deliverability
                payload = {
                    "sender": {
                        "name": self.from_name,
                        "email": self.from_email
                    },
                    "to": recipients,
                    "subject": subject,
                    "headers": {
                        "X-Mailer": "Crane Intelligence Platform",
                        "X-Priority": "1",
                        "List-Unsubscribe": f"<mailto:{self.from_email}?subject=unsubscribe>",
                        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                        "Precedence": "bulk",
                        "X-Auto-Response-Suppress": "All"
                    },
                    "replyTo": {
                        "email": self.from_email,
                        "name": self.from_name
                    }
                }
                
                # Use template ID if provided, otherwise use HTML content
                if template_id:
                    payload["templateId"] = template_id
                    if params:
                        payload["params"] = params
                else:
                    payload["htmlContent"] = html_content
                    if text_content:
                        payload["textContent"] = text_content
                
                # Add reply-to if provided
                if reply_to:
                    payload["replyTo"] = {
                        "email": reply_to
                    }
                
                # Add tags if provided
                if tags:
                    payload["tags"] = tags
                
                # Add custom headers if provided
                if headers:
                    payload["headers"] = headers
                
                # Process attachments
                if attachments:
                    processed_attachments = []
                    for attachment in attachments:
                        if 'file_path' in attachment:
                            # Read file from path
                            with open(attachment['file_path'], 'rb') as f:
                                file_content = f.read()
                                encoded_content = base64.b64encode(file_content).decode('utf-8')
                                processed_attachments.append({
                                    "name": attachment.get('name', os.path.basename(attachment['file_path'])),
                                    "content": encoded_content
                                })
                        elif 'content' in attachment:
                            # Content is already provided (should be base64)
                            processed_attachments.append({
                                "name": attachment.get('name', 'attachment'),
                                "content": attachment['content']
                            })
                    if processed_attachments:
                        payload["attachment"] = processed_attachments
                
                # Send request to Brevo API
                # Log request details (without sensitive data)
                logger.info(f"Sending email via Brevo API to: {to_emails}, Subject: {subject}")
                print(f"📧 Sending email via Brevo API to: {to_emails}")
                
                response = requests.post(
                    f"{self.api_url}/smtp/email",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30
                )
                
                logger.info(f"Brevo API response status: {response.status_code}")
                print(f"📧 Brevo API response status: {response.status_code}")
                
                if response.status_code == 201:
                    result = response.json()
                    message_id = result.get("messageId", "unknown")
                    logger.info(f"✓ Email sent successfully via Brevo to {to_emails}, message ID: {message_id}")
                    print(f"✓ Email sent successfully via Brevo. Message ID: {message_id}")
                    return {
                        "success": True,
                        "message": f"Email sent successfully. Message ID: {message_id}",
                        "message_id": message_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                elif response.status_code == 400:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get('message', response.text)
                    logger.error(f"✗ Brevo API 400 Bad Request: {error_msg}")
                    logger.error(f"Full error response: {error_data}")
                    print(f"✗ Brevo API 400 Bad Request: {error_msg}")
                    return {
                        "success": False,
                        "message": f"Invalid request: {error_msg}",
                        "status_code": response.status_code,
                        "error_details": error_data
                    }
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        retry_after = int(response.headers.get('Retry-After', self.retry_delay * (attempt + 1)))
                        logger.warning(f"Rate limited, retrying after {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                    else:
                        error_msg = response.text
                        logger.error(f"Brevo API rate limit exceeded: {error_msg}")
                        return {
                            "success": False,
                            "message": f"Rate limit exceeded: {error_msg}",
                            "status_code": response.status_code
                        }
                else:
                    error_msg = response.text
                    logger.error(f"Brevo API error {response.status_code}: {error_msg}")
                    last_error = {
                        "success": False,
                        "message": f"Brevo API error: {error_msg}",
                        "status_code": response.status_code
                    }
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return last_error
                    # Retry on server errors (5xx)
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return last_error
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request timeout, retrying... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"Request timeout after {self.max_retries} attempts")
                    return {
                        "success": False,
                        "message": "Request timeout after multiple retries"
                    }
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Network error, retrying... (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"Failed to send email via Brevo API after {self.max_retries} attempts: {e}")
                    return {
                        "success": False,
                        "message": f"Network error: {str(e)}"
                    }
            except Exception as e:
                logger.error(f"Unexpected error sending email via Brevo: {e}")
                return {
                    "success": False,
                    "message": f"Unexpected error: {str(e)}"
                }
        
        return last_error or {
            "success": False,
            "message": "Failed to send email after all retries"
        }
    
    def send_template_email(
        self,
        to_emails: List[str],
        template_name: str,
        template_context: Dict[str, Any],
        subject: Optional[str] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send email using a template
        
        Args:
            to_emails: List of recipient email addresses
            template_name: Name of the template file
            template_context: Context variables for template rendering
            subject: Email subject (if not provided, will use from template context)
            reply_to: Reply-to email address (optional)
            tags: List of tags for email categorization (optional)
            attachments: List of attachment dicts (optional)
        
        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        # Render template
        html_content = self._render_template(template_name, template_context)
        
        # Get subject from context or use default
        email_subject = subject or template_context.get('subject', 'Notification from Crane Intelligence')
        
        # Send email
        return self.send_email(
            to_emails=to_emails,
            subject=email_subject,
            html_content=html_content,
            reply_to=reply_to,
            tags=tags,
            attachments=attachments
        )
    
    def send_batch_emails(
        self,
        email_list: List[Dict[str, Any]],
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Send multiple emails in batches
        
        Args:
            email_list: List of email dicts, each containing:
                - to_emails: List[str]
                - subject: str
                - html_content: str
                - text_content: Optional[str]
                - attachments: Optional[List[Dict]]
                - reply_to: Optional[str]
                - tags: Optional[List[str]]
            batch_size: Number of emails to send per batch
        
        Returns:
            Dict with 'success' (bool), 'total' (int), 'sent' (int), 'failed' (int), 'results' (list)
        """
        total = len(email_list)
        sent = 0
        failed = 0
        results = []
        
        for i in range(0, total, batch_size):
            batch = email_list[i:i + batch_size]
            for email_data in batch:
                result = self.send_email(**email_data)
                results.append(result)
                if result.get("success"):
                    sent += 1
                else:
                    failed += 1
        
        return {
            "success": failed == 0,
            "total": total,
            "sent": sent,
            "failed": failed,
            "results": results
        }
    
    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get email delivery status from Brevo
        
        Args:
            message_id: Brevo message ID
        
        Returns:
            Dict with email status information
        """
        if not self.api_key:
            return {
                "success": False,
                "message": "Brevo API key not configured"
            }
        
        try:
            response = requests.get(
                f"{self.api_url}/smtp/emails/{message_id}",
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to get email status: {response.text}",
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"Error getting email status: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def send_email_async(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        template_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Async wrapper for send_email
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.send_email,
            to_emails,
            subject,
            html_content,
            text_content,
            attachments,
            reply_to,
            tags,
            params,
            headers,
            template_id
        )

