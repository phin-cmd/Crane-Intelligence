#!/usr/bin/env python3
"""
Server Health Monitoring System
Monitors dev, UAT, and production servers and websites
Sends notifications and emails to admins when issues are detected
"""

import requests
import smtplib
import json
import time
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/crane/server-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Server configurations
SERVERS = {
    'dev': {
        'api_url': 'https://dev.craneintelligence.tech/api/v1/health',
        'website_url': 'https://dev.craneintelligence.tech',
        'name': 'Development Server'
    },
    'uat': {
        'api_url': 'https://uat.craneintelligence.tech/api/v1/health',
        'website_url': 'https://uat.craneintelligence.tech',
        'name': 'UAT Server'
    },
    'production': {
        'api_url': 'https://craneintelligence.tech/api/v1/health',
        'website_url': 'https://craneintelligence.tech',
        'name': 'Production Server'
    }
}

# Email configuration (from environment variables) - Using BREVO
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp-relay.brevo.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', os.getenv('MAIL_USERNAME', '99e09b001@smtp-brevo.com'))
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', os.getenv('BREVO_SMTP_PASSWORD', ''))
FROM_EMAIL = os.getenv('FROM_EMAIL', os.getenv('MAIL_FROM_EMAIL', 'pgenerelly@craneintelligence.tech'))

# Admin emails (from environment or database)
ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',') if os.getenv('ADMIN_EMAILS') else []

# API endpoint for storing alerts
ALERT_API_URL = os.getenv('ALERT_API_URL', 'http://localhost:8000/api/v1/admin/alerts')

# Alert state tracking
alert_states = {}  # Track if we've already sent alerts for each server/issue

def check_server_health(server_key: str, config: Dict) -> Dict:
    """Check health of a server and website"""
    results = {
        'server': server_key,
        'name': config['name'],
        'timestamp': datetime.utcnow().isoformat(),
        'api_status': 'unknown',
        'website_status': 'unknown',
        'api_response_time': None,
        'website_response_time': None,
        'api_error': None,
        'website_error': None,
        'overall_status': 'unknown'
    }
    
    # Check API health
    try:
        start_time = time.time()
        response = requests.get(
            config['api_url'],
            timeout=10,
            headers={'User-Agent': 'Crane-Health-Monitor/1.0'}
        )
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            results['api_status'] = 'healthy'
            results['api_response_time'] = round(response_time, 2)
        else:
            results['api_status'] = 'unhealthy'
            results['api_error'] = f'HTTP {response.status_code}'
    except requests.exceptions.Timeout:
        results['api_status'] = 'down'
        results['api_error'] = 'Connection timeout'
    except requests.exceptions.ConnectionError:
        results['api_status'] = 'down'
        results['api_error'] = 'Connection refused'
    except Exception as e:
        results['api_status'] = 'down'
        results['api_error'] = str(e)
        logger.error(f"Error checking API for {server_key}: {e}")
    
    # Check website health
    try:
        start_time = time.time()
        response = requests.get(
            config['website_url'],
            timeout=10,
            headers={'User-Agent': 'Crane-Health-Monitor/1.0'},
            allow_redirects=True
        )
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            results['website_status'] = 'healthy'
            results['website_response_time'] = round(response_time, 2)
        else:
            results['website_status'] = 'unhealthy'
            results['website_error'] = f'HTTP {response.status_code}'
    except requests.exceptions.Timeout:
        results['website_status'] = 'down'
        results['website_error'] = 'Connection timeout'
    except requests.exceptions.ConnectionError:
        results['website_status'] = 'down'
        results['website_error'] = 'Connection refused'
    except Exception as e:
        results['website_status'] = 'down'
        results['website_error'] = str(e)
        logger.error(f"Error checking website for {server_key}: {e}")
    
    # Determine overall status
    if results['api_status'] in ['healthy', 'unhealthy'] and results['website_status'] in ['healthy', 'unhealthy']:
        if results['api_status'] == 'healthy' and results['website_status'] == 'healthy':
            results['overall_status'] = 'healthy'
        else:
            results['overall_status'] = 'degraded'
    elif results['api_status'] == 'down' or results['website_status'] == 'down':
        results['overall_status'] = 'down'
    else:
        results['overall_status'] = 'unknown'
    
    return results

def send_email_alert(server_name: str, issues: List[str], admin_emails: List[str]):
    """Send email alert to admins"""
    if not admin_emails or not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Email configuration missing, skipping email alert")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = ', '.join(admin_emails)
        msg['Subject'] = f'🚨 ALERT: {server_name} Server Issues Detected'
        
        body = f"""
CRITICAL SERVER ALERT

Server: {server_name}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Issues Detected:
{chr(10).join(f'  • {issue}' for issue in issues)}

Please investigate immediately.

---
Crane Intelligence Server Monitoring System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email alert sent to {len(admin_emails)} admins for {server_name}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")

def send_api_alert(server_key: str, results: Dict):
    """Send alert to API endpoint for dashboard display"""
    try:
        alert_data = {
            'server': server_key,
            'server_name': results['name'],
            'status': results['overall_status'],
            'api_status': results['api_status'],
            'website_status': results['website_status'],
            'api_error': results.get('api_error'),
            'website_error': results.get('website_error'),
            'timestamp': results['timestamp']
        }
        
        response = requests.post(
            ALERT_API_URL,
            json=alert_data,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            logger.info(f"Alert sent to API for {server_key}")
        else:
            logger.warning(f"Failed to send alert to API: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending alert to API: {e}")

def should_send_alert(server_key: str, issue_type: str, status: str) -> bool:
    """Check if we should send an alert (avoid duplicate alerts)"""
    alert_key = f"{server_key}_{issue_type}"
    
    # If status changed from healthy to unhealthy/down, send alert
    if status in ['down', 'unhealthy']:
        if alert_key not in alert_states or alert_states[alert_key] != status:
            alert_states[alert_key] = status
            return True
    
    # If status recovered, update state but don't send alert (or send recovery notification)
    if status == 'healthy' and alert_key in alert_states:
        previous_status = alert_states[alert_key]
        alert_states[alert_key] = status
        if previous_status in ['down', 'unhealthy']:
            # Optionally send recovery notification
            logger.info(f"{server_key} {issue_type} recovered")
    
    return False

def monitor_all_servers():
    """Monitor all configured servers"""
    all_results = []
    critical_issues = []
    
    for server_key, config in SERVERS.items():
        logger.info(f"Checking {config['name']}...")
        results = check_server_health(server_key, config)
        all_results.append(results)
        
        # Check for issues
        issues = []
        
        if results['api_status'] == 'down':
            if should_send_alert(server_key, 'api', 'down'):
                issues.append(f"API is DOWN: {results.get('api_error', 'Unknown error')}")
        
        if results['website_status'] == 'down':
            if should_send_alert(server_key, 'website', 'down'):
                issues.append(f"Website is DOWN: {results.get('website_error', 'Unknown error')}")
        
        if results['api_status'] == 'unhealthy':
            if should_send_alert(server_key, 'api', 'unhealthy'):
                issues.append(f"API is UNHEALTHY: {results.get('api_error', 'Unknown error')}")
        
        if results['website_status'] == 'unhealthy':
            if should_send_alert(server_key, 'website', 'unhealthy'):
                issues.append(f"Website is UNHEALTHY: {results.get('website_error', 'Unknown error')}")
        
        if issues:
            critical_issues.append({
                'server': config['name'],
                'issues': issues
            })
            
            # Send email alert
            send_email_alert(config['name'], issues, ADMIN_EMAILS)
            
            # Send API alert for dashboard
            send_api_alert(server_key, results)
    
    return all_results, critical_issues

def main():
    """Main monitoring loop"""
    logger.info("Starting server monitoring system...")
    
    # Load admin emails from database if available
    # For now, use environment variable
    if not ADMIN_EMAILS:
        logger.warning("No admin emails configured. Alerts will not be sent via email.")
    
    while True:
        try:
            results, issues = monitor_all_servers()
            
            if issues:
                logger.warning(f"Critical issues detected: {len(issues)} servers affected")
                for issue in issues:
                    logger.warning(f"  - {issue['server']}: {', '.join(issue['issues'])}")
            else:
                logger.info("All servers are healthy")
            
            # Wait before next check (check every 60 seconds)
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    main()

