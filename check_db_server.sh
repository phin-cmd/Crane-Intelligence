#!/bin/bash
# Script to check database server - Run this ON the database server (129.212.177.131)

echo "🔍 PostgreSQL Database Server Diagnostics"
echo "=========================================="
echo ""
echo "Run this script ON the database server (129.212.177.131)"
echo ""

# Check if PostgreSQL is installed
echo "1. Checking PostgreSQL installation..."
if command -v psql >/dev/null 2>&1; then
    PSQL_VERSION=$(psql --version)
    echo "   ✅ PostgreSQL is installed: $PSQL_VERSION"
else
    echo "   ❌ PostgreSQL (psql) is not installed"
    echo "   Install with: sudo apt-get install postgresql postgresql-contrib"
fi

# Check PostgreSQL service status
echo ""
echo "2. Checking PostgreSQL service status..."
if systemctl is-active --quiet postgresql; then
    echo "   ✅ PostgreSQL service is RUNNING"
    systemctl status postgresql --no-pager | head -5
elif systemctl is-active --quiet postgresql@*; then
    echo "   ✅ PostgreSQL service is RUNNING (version-specific)"
    systemctl status postgresql@* --no-pager | head -5
else
    echo "   ❌ PostgreSQL service is NOT RUNNING"
    echo "   Start with: sudo systemctl start postgresql"
    echo "   Enable with: sudo systemctl enable postgresql"
fi

# Check if PostgreSQL is listening
echo ""
echo "3. Checking if PostgreSQL is listening on port 5432..."
if ss -tlnp 2>/dev/null | grep -q ":5432"; then
    echo "   ✅ PostgreSQL is listening on port 5432"
    echo "   Listening addresses:"
    ss -tlnp 2>/dev/null | grep ":5432" | awk '{print "     " $4}'
elif netstat -tlnp 2>/dev/null | grep -q ":5432"; then
    echo "   ✅ PostgreSQL is listening on port 5432"
    echo "   Listening addresses:"
    netstat -tlnp 2>/dev/null | grep ":5432" | awk '{print "     " $4}'
else
    echo "   ❌ PostgreSQL is NOT listening on port 5432"
    echo "   Check postgresql.conf: listen_addresses = '*'"
fi

# Check firewall
echo ""
echo "4. Checking firewall status..."
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "   UFW Status: $UFW_STATUS"
    if sudo ufw status 2>/dev/null | grep -q "5432"; then
        echo "   ✅ Port 5432 is allowed in firewall"
    else
        echo "   ⚠️  Port 5432 might not be allowed"
        echo "   Allow with: sudo ufw allow 5432/tcp"
    fi
elif command -v firewall-cmd >/dev/null 2>&1; then
    echo "   Checking firewalld..."
    if sudo firewall-cmd --list-ports 2>/dev/null | grep -q "5432"; then
        echo "   ✅ Port 5432 is allowed in firewall"
    else
        echo "   ⚠️  Port 5432 might not be allowed"
        echo "   Allow with: sudo firewall-cmd --add-port=5432/tcp --permanent"
    fi
else
    echo "   ⚠️  No firewall management tool found (ufw/firewalld)"
fi

# Check PostgreSQL configuration
echo ""
echo "5. Checking PostgreSQL configuration..."
PG_CONF=$(find /etc/postgresql -name "postgresql.conf" 2>/dev/null | head -1)
if [ -n "$PG_CONF" ]; then
    echo "   Found config: $PG_CONF"
    if grep -q "listen_addresses.*=" "$PG_CONF" 2>/dev/null; then
        LISTEN_ADDR=$(grep "^listen_addresses" "$PG_CONF" 2>/dev/null | head -1)
        echo "   $LISTEN_ADDR"
        if echo "$LISTEN_ADDR" | grep -q "'\*'\|localhost"; then
            echo "   ✅ PostgreSQL is configured to listen on all addresses"
        else
            echo "   ⚠️  PostgreSQL might not be listening on all addresses"
            echo "   Should be: listen_addresses = '*'"
        fi
    else
        echo "   ⚠️  listen_addresses not found in config"
    fi
else
    echo "   ⚠️  Could not find postgresql.conf"
fi

# Check pg_hba.conf
echo ""
echo "6. Checking client authentication (pg_hba.conf)..."
PG_HBA=$(find /etc/postgresql -name "pg_hba.conf" 2>/dev/null | head -1)
if [ -n "$PG_HBA" ]; then
    echo "   Found config: $PG_HBA"
    if grep -q "^host.*all.*all.*0.0.0.0/0" "$PG_HBA" 2>/dev/null; then
        echo "   ✅ Remote connections are allowed"
        grep "^host.*all.*all.*0.0.0.0/0" "$PG_HBA" 2>/dev/null | head -3
    else
        echo "   ⚠️  Remote connections might not be allowed"
        echo "   Add this line to pg_hba.conf:"
        echo "   host    all    all    0.0.0.0/0    md5"
    fi
else
    echo "   ⚠️  Could not find pg_hba.conf"
fi

echo ""
echo "=========================================="
echo "Next steps:"
echo "1. If PostgreSQL is not running: sudo systemctl start postgresql"
echo "2. If not listening: Edit postgresql.conf and set listen_addresses = '*'"
echo "3. If firewall blocking: sudo ufw allow 5432/tcp"
echo "4. If auth blocking: Edit pg_hba.conf and add remote access rule"
echo "5. After changes: sudo systemctl restart postgresql"

