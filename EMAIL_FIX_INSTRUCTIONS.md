# Email Fix Instructions

## Current Status
✅ **Code is fixed and working correctly**
❌ **Network/Firewall blocking SMTP connections**

## The Problem
The server cannot reach `smtp-relay.brevo.com:587` due to firewall restrictions. This is blocking all email sending.

## Solution Steps

### 1. Check Cloud Provider Firewall
If you're using DigitalOcean, AWS, Azure, etc., check their firewall/security group settings:

**DigitalOcean:**
- Go to Networking → Firewalls
- Create/edit firewall rules
- Add outbound rule: Allow TCP port 587 to `smtp-relay.brevo.com`
- Apply firewall to your droplet

**AWS:**
- Go to EC2 → Security Groups
- Edit outbound rules
- Add: Allow TCP port 587 to `0.0.0.0/0` (or specific IP)

**General:**
- Allow outbound TCP port 587
- Allow outbound TCP port 465 (backup)
- Destination: `smtp-relay.brevo.com` or `0.0.0.0/0`

### 2. Test Connectivity
After updating firewall, test:

```bash
# From host
timeout 10 bash -c 'echo > /dev/tcp/smtp-relay.brevo.com/587' && echo "✅ Accessible" || echo "❌ Still blocked"

# From container
docker compose exec backend python3 -c "
import socket
sock = socket.socket()
sock.settimeout(10)
try:
    sock.connect(('smtp-relay.brevo.com', 587))
    print('✅ SMTP port accessible')
    sock.close()
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 3. Alternative: Use Brevo API
If SMTP ports cannot be opened, get a valid Brevo Transactional API key:

1. Log into Brevo Dashboard: https://app.brevo.com/
2. Go to Settings → SMTP & API
3. Create a **Transactional API Key** (starts with `xkeysib-`)
4. Update `docker-compose.yml`:
   ```yaml
   - USE_BREVO_API=true
   - BREVO_API_KEY=<your-transactional-api-key>
   ```
5. Restart backend: `docker compose restart backend`

## Current Configuration (SMTP)
- Server: `smtp-relay.brevo.com`
- Port: `587`
- Username: `99e09b001@smtp-brevo.com`
- Password: `CraneIntel123!`
- From: `pgenerelly@craneintelligence.tech`
- `USE_BREVO_API=false`

## Verification
Once firewall is fixed, create a test draft report and check:
```bash
docker compose logs backend | grep -i "email sent\|smtp"
```

You should see: `Email sent successfully to [email]`

