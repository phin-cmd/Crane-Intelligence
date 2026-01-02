# Quick Deploy & Sync Guide

## One Command to Deploy Everything

To deploy code and sync database from Production to both UAT and DEV:

```bash
cd /root/crane
./scripts/deployment/sync-prod-to-all-environments.sh
```

**That's it!** This single command will:
1. ✅ Backup UAT and DEV databases
2. ✅ Sync production database to UAT
3. ✅ Sync production database to DEV
4. ✅ Deploy production code to UAT
5. ✅ Deploy production code to DEV
6. ✅ Restart all services

## What You'll See

The script will:
- Ask for confirmation (type `yes` to proceed)
- Show progress for each step
- Create automatic backups
- Verify each step completed successfully

## After Running

### 1. Verify Services

```bash
docker ps | grep backend
```

Should show all three backends running.

### 2. Test Endpoints

```bash
# DEV
curl http://localhost:8104/api/v1/config/public

# UAT
curl http://localhost:8204/api/v1/config/public
```

### 3. Test Payment Flow

```bash
./scripts/test-complete-payment-flow.sh dev
./scripts/test-complete-payment-flow.sh uat
```

## Important Notes

⚠️ **WARNING**: This will OVERWRITE UAT and DEV databases with production data!

✅ **Safety**: Automatic backups are created before any changes

✅ **Recovery**: Backups are saved to `/root/crane/backups/` with timestamps

## Need Help?

See `DEPLOYMENT_AND_SYNC_GUIDE.md` for detailed documentation.

