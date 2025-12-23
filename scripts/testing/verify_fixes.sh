#!/bin/bash
echo "=== Production Fixes Verification ==="
echo ""

echo "1. ✅ Email Configuration:"
cd backend
if grep -q "BREVO_API_KEY=your-brevo-api-key-here" .env; then
    echo "   ✓ Brevo API key configured"
else
    echo "   ✗ Brevo API key missing or incorrect"
fi
if grep -q "USE_BREVO_API=true" .env; then
    echo "   ✓ USE_BREVO_API enabled"
else
    echo "   ✗ USE_BREVO_API not enabled"
fi
cd ..

echo ""
echo "2. ✅ File Upload Fix:"
if grep -q "report_id: Optional\[int\] = Form(None)" backend/app/api/v1/fmv_reports.py; then
    echo "   ✓ Backend accepts report_id parameter"
else
    echo "   ✗ Backend missing report_id parameter"
fi
if grep -q "formData.append(\"report_id\"" report-generation.html; then
    echo "   ✓ Frontend sends report_id"
else
    echo "   ✗ Frontend not sending report_id"
fi

echo ""
echo "3. ✅ Modal Close Button:"
if grep -q "top: 20px" dashboard.html && grep -q "right: 20px" dashboard.html; then
    echo "   ✓ Close button positioned at top right"
else
    echo "   ✗ Close button position incorrect"
fi

echo ""
echo "4. ✅ Payment Modal:"
if grep -q "setProperty.*display.*flex.*important" report-generation.html; then
    echo "   ✓ Payment modal visibility fixed"
else
    echo "   ✗ Payment modal fix missing"
fi

echo ""
echo "5. ✅ Delete Function:"
if grep -q "localStorage.getItem.*access_token" dashboard.html; then
    echo "   ✓ Delete function checks localStorage"
else
    echo "   ✗ Delete function missing localStorage check"
fi
if grep -q "/api/v1/fmv-reports/\${draftId}/delete" dashboard.html; then
    echo "   ✓ Delete uses relative URL"
else
    echo "   ✗ Delete URL incorrect"
fi

echo ""
echo "=== IMPORTANT: Next Steps ==="
echo "1. Restart backend server to load .env changes"
echo "2. Clear browser cache or hard refresh (Ctrl+Shift+R)"
echo "3. Test the complete flow"
