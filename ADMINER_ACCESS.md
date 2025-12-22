# Adminer Database Access Details

## Overview

Adminer is a lightweight database management tool accessible via web browser. Each environment has its own Adminer instance with isolated database access.

---

## Development Environment

### Access URL
- **Local (from server)**: http://localhost:8182
- **External (if exposed)**: http://dev.craneintelligence.tech:8182
- **Direct IP**: http://129.212.177.131:8182

### Database Connection Details
- **System**: PostgreSQL
- **Server**: `db` (or `localhost` if connecting from outside container)
- **Username**: `crane_dev_user`
- **Password**: `crane_dev_password`
- **Database**: `crane_intelligence_dev`

### Login Steps
1. Open Adminer URL in browser
2. Select **PostgreSQL** from the System dropdown
3. Enter:
   - **Server**: `db` (or `crane-dev-db-1` if connecting from host)
   - **Username**: `crane_dev_user`
   - **Password**: `crane_dev_password`
   - **Database**: `crane_intelligence_dev`
4. Click **Login**

### Direct Database Connection (from server)
```bash
# Via Docker exec
docker compose -f docker-compose.dev.yml -p crane-dev exec db \
  psql -U crane_dev_user -d crane_intelligence_dev

# Via host port (if exposed)
psql -h localhost -p 5534 -U crane_dev_user -d crane_intelligence_dev
```

---

## UAT Environment

### Access URL
- **Local (from server)**: http://localhost:8282
- **External (if exposed)**: http://uat.craneintelligence.tech:8282
- **Direct IP**: http://129.212.177.131:8282

### Database Connection Details
- **System**: PostgreSQL
- **Server**: `db` (or `localhost` if connecting from outside container)
- **Username**: `crane_uat_user`
- **Password**: `crane_uat_password`
- **Database**: `crane_intelligence_uat`

### Login Steps
1. Open Adminer URL in browser
2. Select **PostgreSQL** from the System dropdown
3. Enter:
   - **Server**: `db` (or `crane-uat-db-1` if connecting from host)
   - **Username**: `crane_uat_user`
   - **Password**: `crane_uat_password`
   - **Database**: `crane_intelligence_uat`
4. Click **Login**

### Direct Database Connection (from server)
```bash
# Via Docker exec
docker compose -f docker-compose.uat.yml -p crane-uat exec db \
  psql -U crane_uat_user -d crane_intelligence_uat

# Via host port (if exposed)
psql -h localhost -p 5634 -U crane_uat_user -d crane_intelligence_uat
```

---

## Production Environment

### Access URL
- **Local (from server)**: http://localhost:8082
- **External (if exposed)**: http://craneintelligence.tech:8082
- **Direct IP**: http://129.212.177.131:8082

### Database Connection Details
- **System**: PostgreSQL
- **Server**: `db` (or `localhost` if connecting from outside container)
- **Username**: `crane_user`
- **Password**: `crane_password`
- **Database**: `crane_intelligence`

### Login Steps
1. Open Adminer URL in browser
2. Select **PostgreSQL** from the System dropdown
3. Enter:
   - **Server**: `db` (or `crane_db_1` if connecting from host)
   - **Username**: `crane_user`
   - **Password**: `crane_password`
   - **Database**: `crane_intelligence`
4. Click **Login**

### Direct Database Connection (from server)
```bash
# Via Docker exec
docker compose exec db psql -U crane_user -d crane_intelligence

# Via host port (if exposed)
psql -h localhost -p 5434 -U crane_user -d crane_intelligence
```

---

## Quick Reference Table

| Environment | Adminer Port | Database Port | Username | Password | Database Name |
|------------|--------------|---------------|----------|----------|---------------|
| **Dev** | 8182 | 5534 | `crane_dev_user` | `crane_dev_password` | `crane_intelligence_dev` |
| **UAT** | 8282 | 5634 | `crane_uat_user` | `crane_uat_password` | `crane_intelligence_uat` |
| **Prod** | 8082 | 5434 | `crane_user` | `crane_password` | `crane_intelligence` |

---

## Security Notes

### ⚠️ Important Security Considerations

1. **Adminer ports are NOT exposed via HTTPS** - They're HTTP only
2. **Consider restricting access** - Use firewall rules to limit Adminer access to trusted IPs
3. **Production access** - Be extra careful with production database access
4. **Password security** - These passwords are in docker-compose files; consider using secrets management

### Recommended: Restrict Adminer Access

To restrict Adminer to localhost only, you can:

1. **Remove port mappings** from docker-compose files (access only via `docker exec`)
2. **Use SSH tunnel** to access Adminer:
   ```bash
   ssh -L 8182:localhost:8182 root@your-server-ip
   # Then access http://localhost:8182 in your browser
   ```
3. **Add Nginx authentication** - Create a reverse proxy with basic auth

### Example: SSH Tunnel Setup

```bash
# For Dev Adminer
ssh -L 8182:localhost:8182 root@129.212.177.131

# For UAT Adminer
ssh -L 8282:localhost:8282 root@129.212.177.131

# For Prod Adminer
ssh -L 8082:localhost:8082 root@129.212.177.131
```

Then access `http://localhost:8182` (or 8282, 8082) in your browser.

---

## Troubleshooting

### Cannot connect to Adminer

1. **Check if container is running**:
   ```bash
   # Dev
   docker compose -f docker-compose.dev.yml -p crane-dev ps adminer
   
   # UAT
   docker compose -f docker-compose.uat.yml -p crane-uat ps adminer
   
   # Prod
   docker compose ps adminer
   ```

2. **Check Adminer logs**:
   ```bash
   docker compose -f docker-compose.dev.yml -p crane-dev logs adminer
   ```

3. **Verify database is accessible**:
   ```bash
   docker compose -f docker-compose.dev.yml -p crane-dev exec db pg_isready -U crane_dev_user
   ```

### Connection refused errors

- Ensure the Adminer container is running
- Check if the port is already in use: `netstat -tulpn | grep 8182`
- Verify firewall rules allow the port

### Authentication failed

- Double-check username and password
- Ensure database exists: `docker compose -f docker-compose.dev.yml -p crane-dev exec db psql -U crane_dev_user -l`

---

## Alternative: Direct psql Access

If you prefer command-line access:

```bash
# Dev
docker compose -f docker-compose.dev.yml -p crane-dev exec db psql -U crane_dev_user -d crane_intelligence_dev

# UAT
docker compose -f docker-compose.uat.yml -p crane-uat exec db psql -U crane_uat_user -d crane_intelligence_uat

# Prod
docker compose exec db psql -U crane_user -d crane_intelligence
```

---

## Useful Adminer Features

- **SQL Command**: Run custom SQL queries
- **Export**: Export database structure and data
- **Import**: Import SQL files
- **Browse**: View and edit table data
- **Structure**: View database schema
- **Privileges**: Manage user permissions

---

Last updated: Thu Dec 18 23:31:55 UTC 2025

