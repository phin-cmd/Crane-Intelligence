# Fix "No such file or directory" Error

## Problem

When running scripts, you might see:
```bash
bash: ./test_security.sh: No such file or directory
bash: ./monitor_security.sh: No such file or directory
bash: ./restart-backend-secure.sh: No such file or directory
```

## Solution

### Option 1: Ensure You're in the Correct Directory

```bash
# Navigate to the crane directory
cd /root/crane

# Verify scripts exist
ls -la test_security.sh monitor_security.sh restart-backend-secure.sh

# Run scripts
./test_security.sh
./monitor_security.sh
./restart-backend-secure.sh
```

### Option 2: Use Full Path

```bash
# Run from anywhere using full path
/root/crane/test_security.sh http://localhost:8004
/root/crane/monitor_security.sh monitor
/root/crane/restart-backend-secure.sh
```

### Option 3: Use the Helper Script

```bash
# From anywhere, use the helper script
/root/crane/run-security-scripts.sh test http://localhost:8004
/root/crane/run-security-scripts.sh monitor monitor
/root/crane/run-security-scripts.sh restart
```

### Option 4: Create Aliases (Add to ~/.bashrc)

```bash
# Add these lines to ~/.bashrc
alias test-security='/root/crane/test_security.sh'
alias monitor-security='/root/crane/monitor_security.sh'
alias restart-backend='/root/crane/restart-backend-secure.sh'

# Then reload
source ~/.bashrc

# Now you can use from anywhere:
test-security http://localhost:8004
monitor-security monitor
restart-backend
```

## Verify Scripts Exist

Run the verification script:

```bash
cd /root/crane
./verify-scripts.sh
```

This will:
- Check if all scripts exist
- Fix permissions if needed
- Report any missing scripts

## Quick Fix Command

```bash
# Fix all at once
cd /root/crane && \
chmod +x test_security.sh monitor_security.sh restart-backend-secure.sh && \
./verify-scripts.sh
```

## Script Locations

All scripts are located in: `/root/crane/`

- `test_security.sh` - Security testing
- `monitor_security.sh` - Security monitoring
- `restart-backend-secure.sh` - Secure backend restart
- `verify-scripts.sh` - Verify all scripts
- `run-security-scripts.sh` - Helper to run from anywhere

## Common Issues

### Issue: "Permission denied"
**Fix:**
```bash
chmod +x /root/crane/*.sh
```

### Issue: "No such file or directory"
**Fix:**
```bash
# Make sure you're in the right directory
cd /root/crane
pwd  # Should show /root/crane

# Or use full path
/root/crane/test_security.sh
```

### Issue: Scripts not executable
**Fix:**
```bash
cd /root/crane
chmod +x test_security.sh monitor_security.sh restart-backend-secure.sh
```

## Verification

After fixing, verify:

```bash
cd /root/crane
ls -la *.sh | grep -E "test_security|monitor_security|restart-backend"
```

All should show `-rwxr-xr-x` (executable).

