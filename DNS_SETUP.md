# DNS Setup for Dev and UAT Environments

## Required DNS Records

To enable `https://dev.craneintelligence.tech/` and `https://uat.craneintelligence.tech/`, you need to add the following DNS records in your domain registrar (where `craneintelligence.tech` is managed):

### A Records

Add these A records pointing to your server's IP address:

```
Type: A
Name: dev
Value: <your-server-ip>  (e.g., 129.212.177.131)
TTL: 3600 (or default)

Type: A
Name: uat
Value: <your-server-ip>  (e.g., 129.212.177.131)
TTL: 3600 (or default)
```

This will create:
- `dev.craneintelligence.tech` → your server IP
- `uat.craneintelligence.tech` → your server IP

## Verification

After adding DNS records, wait 5-15 minutes for propagation, then verify:

```bash
# Check DNS resolution
dig dev.craneintelligence.tech +short
dig uat.craneintelligence.tech +short

# Both should return your server's IP address
```

## SSL Certificate Setup

Once DNS is configured and resolving correctly, run:

```bash
/root/crane/setup-ssl-subdomains.sh
```

This script will:
1. Obtain Let's Encrypt SSL certificates for both subdomains
2. Update Nginx configs to use the new certificates
3. Enable HTTPS redirects
4. Reload Nginx

## Testing

After DNS and SSL are set up, test the environments:

```bash
# Test dev environment
curl -I https://dev.craneintelligence.tech/
curl -I https://dev.craneintelligence.tech/api/

# Test UAT environment
curl -I https://uat.craneintelligence.tech/
curl -I https://uat.craneintelligence.tech/api/
```

Both should return `HTTP/1.1 200 OK` responses.

