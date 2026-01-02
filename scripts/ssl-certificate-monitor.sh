#!/bin/bash
# SSL Certificate Monitoring Script
# Checks certificate validity and alerts if issues are detected

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Domains to check
DOMAINS=(
    "craneintelligence.tech"
    "www.craneintelligence.tech"
    "dev.craneintelligence.tech"
    "uat.craneintelligence.tech"
)

# Email for alerts (if configured)
ALERT_EMAIL="${ALERT_EMAIL:-pgenerelly@craneintelligence.tech}"

# Function to check certificate
check_certificate() {
    local domain=$1
    local port=${2:-443}
    
    echo -n "Checking $domain... "
    
    # Get certificate info
    local cert_info=$(echo | openssl s_client -connect "${domain}:${port}" -servername "$domain" 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null)
    
    if [ -z "$cert_info" ]; then
        echo -e "${RED}✗ Cannot connect${NC}"
        return 1
    fi
    
    # Check issuer
    local issuer=$(echo "$cert_info" | grep "issuer=" | cut -d'=' -f2-)
    
    if echo "$issuer" | grep -q "Let's Encrypt"; then
        echo -e "${GREEN}✓ Valid Let's Encrypt certificate${NC}"
        
        # Check expiration
        local not_after=$(echo "$cert_info" | grep "notAfter=" | cut -d'=' -f2)
        local expiry_date=$(date -d "$not_after" +%s 2>/dev/null || echo "0")
        local current_date=$(date +%s)
        local days_until_expiry=$(( (expiry_date - current_date) / 86400 ))
        
        if [ $days_until_expiry -lt 30 ]; then
            echo -e "  ${RED}⚠ WARNING: Certificate expires in $days_until_expiry days!${NC}"
            return 2
        elif [ $days_until_expiry -lt 60 ]; then
            echo -e "  ${YELLOW}⚠ Certificate expires in $days_until_expiry days${NC}"
        else
            echo -e "  ${GREEN}✓ Certificate valid for $days_until_expiry days${NC}"
        fi
        
        return 0
    elif echo "$issuer" | grep -q "Crane Intelligence"; then
        echo -e "${RED}✗ SELF-SIGNED CERTIFICATE DETECTED!${NC}"
        echo -e "  ${RED}This is a critical security issue!${NC}"
        return 3
    else
        echo -e "${YELLOW}⚠ Unknown certificate issuer: $issuer${NC}"
        return 1
    fi
}

# Function to verify certificate chain
verify_certificate() {
    local domain=$1
    
    local verify_code=$(echo | openssl s_client -connect "${domain}:443" -servername "$domain" 2>/dev/null | grep "Verify return code" | awk '{print $4}')
    
    if [ "$verify_code" = "0" ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
echo "=========================================="
echo "SSL Certificate Monitoring"
echo "=========================================="
echo ""

ISSUES_FOUND=0
CRITICAL_ISSUES=0

for domain in "${DOMAINS[@]}"; do
    check_certificate "$domain"
    cert_status=$?
    
    if [ $cert_status -eq 3 ]; then
        CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
    elif [ $cert_status -ne 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
    
    # Verify certificate chain
    if ! verify_certificate "$domain"; then
        echo -e "  ${RED}✗ Certificate verification failed${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
    
    echo ""
done

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""

if [ $CRITICAL_ISSUES -gt 0 ]; then
    echo -e "${RED}CRITICAL: $CRITICAL_ISSUES self-signed certificate(s) detected!${NC}"
    echo ""
    echo "Immediate action required:"
    echo "1. Run: certbot renew --force-renewal"
    echo "2. Restart nginx: systemctl restart nginx"
    echo "3. Verify: ./scripts/ssl-certificate-monitor.sh"
    exit 2
elif [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "${YELLOW}WARNING: $ISSUES_FOUND issue(s) found${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All certificates are valid${NC}"
    exit 0
fi

