#!/bin/bash
echo "=========================================="
echo "Security Setup Verification"
echo "=========================================="
echo ""

# Check environment variable
if grep -q "ENVIRONMENT=production" config/prod.env 2>/dev/null || grep -q "ENVIRONMENT=production" backend/.env 2>/dev/null; then
    echo "✅ ENVIRONMENT=production is set"
else
    echo "⚠️  ENVIRONMENT=production not found"
    echo "   Run: echo 'ENVIRONMENT=production' >> config/prod.env"
fi

# Check security files exist
echo ""
echo "Checking security files..."
[ -f backend/app/security/payment_validator.py ] && echo "✅ Payment validator exists" || echo "❌ Payment validator missing"
[ -f backend/app/security/bot_detector.py ] && echo "✅ Bot detector exists" || echo "❌ Bot detector missing"
[ -f backend/app/security/audit_logger.py ] && echo "✅ Audit logger exists" || echo "❌ Audit logger missing"
[ -f test_security.sh ] && echo "✅ Security test script exists" || echo "❌ Security test script missing"
[ -f monitor_security.sh ] && echo "✅ Security monitor script exists" || echo "❌ Security monitor script missing"

# Check nginx config
echo ""
echo "Checking nginx configuration..."
if grep -q "X-Frame-Options" nginx.conf 2>/dev/null; then
    echo "✅ Security headers configured in nginx"
else
    echo "⚠️  Security headers not found in nginx.conf"
fi

if grep -q "limit_req" nginx.conf 2>/dev/null; then
    echo "✅ Rate limiting configured in nginx"
else
    echo "⚠️  Rate limiting not found in nginx.conf"
fi

echo ""
echo "=========================================="
echo "Verification complete!"
echo "=========================================="
