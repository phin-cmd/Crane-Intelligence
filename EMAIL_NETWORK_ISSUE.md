# Email Not Working - Network/Firewall Issue

## Problem
Emails are not being sent because **all SMTP ports are blocked** from the Docker container.

## Test Results
- ❌ Port 587 (SMTP with TLS) - CLOSED
- ❌ Port 465 (SMTP with SSL) - CLOSED  
- ❌ Port 25 (SMTP) - CLOSED
- ❌ Connection timeout after 30 seconds

## Root Cause
The Docker container cannot reach `smtp-relay.brevo.com` on any SMTP port. This is a **network/firewall configuration issue**, not a code issue.

## Code Status
✅ All code fixes are complete:
- `FMVEmailService` uses `UnifiedEmailService`
- `UnifiedEmailService` has `send_template_email` method
- Configuration: `USE_BREVO_API=false` (using SMTP)
- Email sending code is being called correctly

## Solutions

### Option 1: Open Firewall Ports (Recommended)
Allow outbound SMTP connections from the server:

```bash
# If using UFW
sudo ufw allow out 587/tcp
sudo ufw allow out 465/tcp

# If using iptables
sudo iptables -A OUTPUT -p tcp --dport 587 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 465 -j ACCEPT
```

### Option 2: Use Host Network Mode
Modify `docker-compose.yml` to use host network:

```yaml
backend:
  network_mode: "host"
```

### Option 3: Use Brevo API (If Valid Key Available)
If you can get a valid Brevo Transactional API key (starts with `xkeysib-`), set:
- `USE_BREVO_API=true`
- `BREVO_API_KEY=<valid-api-key>`

### Option 4: Use SMTP Relay/Proxy
Set up an SMTP relay on the host that can reach Brevo, then configure the container to use `localhost:25` or `host.docker.internal:587`.

## Current Configuration
- SMTP Server: `smtp-relay.brevo.com`
- Port: `587`
- Username: `99e09b001@smtp-brevo.com`
- Password: `CraneIntel123!`
- From: `pgenerelly@craneintelligence.tech`

## Next Steps
1. **Check server firewall rules** - Allow outbound port 587
2. **Check cloud provider firewall** - DigitalOcean/AWS/etc may have network security groups blocking SMTP
3. **Test from host** - Verify if the issue is Docker-specific or server-wide
4. **Contact hosting provider** - Some providers block SMTP ports by default

## Verification
After fixing firewall, test with:
```bash
docker compose exec backend python3 -c "
from app.services.email_service_unified import UnifiedEmailService
service = UnifiedEmailService()
result = service.send_email(['test@example.com'], 'Test', '<p>Test</p>')
print('Result:', result)
"
```

