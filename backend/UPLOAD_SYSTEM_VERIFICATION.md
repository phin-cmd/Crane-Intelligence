# DigitalOcean Spaces Upload System Verification Guide

## Changes Applied

### 1. Storage Service Enhancements (`app/services/storage_service.py`)
- ✅ Enhanced `get_storage_service()` with re-initialization logic
- ✅ Better error handling if `s3_client` is None
- ✅ Detailed initialization logging (bucket, region, environment, endpoints)
- ✅ Credential status logging (masked for security)

### 2. Upload Endpoints Enhancements (`app/api/v1/fmv_reports.py`)
- ✅ Enhanced `/upload-service-records` endpoint with better error handling
- ✅ Enhanced `/upload-bulk-file` endpoint with better error handling
- ✅ Detailed error messages showing credential status
- ✅ Proper exception handling for both endpoints

## Verification Steps

### Step 1: Restart Backend

```bash
# Stop existing backend
pkill -f "uvicorn.*main:app"

# Start backend with proper environment
cd /root/crane/backend
bash start_backend.sh

# Or manually:
# Set these in your .env file (not committed to git):
# export DO_SPACES_KEY=your_key_here
# export DO_SPACES_SECRET=your_secret_here
export DO_SPACES_REGION=atl1
export DO_SPACES_BUCKET=crane-intelligence-storage
export ENVIRONMENT=prod

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### Step 2: Check Backend Logs for Initialization

Look for these log messages in the backend output:

```
✅ DigitalOcean Spaces client initialized successfully:
   Bucket: crane-intelligence-storage
   Region: atl1
   Environment: prod
   Endpoint: https://atl1.digitaloceanspaces.com
   CDN Endpoint: https://crane-intelligence-storage.atl1.digitaloceanspaces.com
   Access Key: DO00VXHWPGK... (masked)
```

If you see errors like:
- `❌ Storage service s3_client is None` - Check credentials
- `❌ Failed to initialize storage service` - Check boto3 installation

### Step 3: Test Storage Service Initialization

Run the test script:

```bash
cd /root/crane/backend
python3 test_storage_upload.py
```

Expected output:
```
✅ Storage service created
✅ s3_client initialized
✅ Upload successful!
CDN URL: https://crane-intelligence-storage.atl1.digitaloceanspaces.com/prod/test-uploads/...
```

### Step 4: Test File Upload via API

#### Test Service Records Upload:

```bash
# Create a test file
echo "Test content" > /tmp/test.pdf

# Upload via API (replace TOKEN with actual auth token)
curl -X POST http://localhost:8004/api/v1/fmv-reports/upload-service-records \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/tmp/test.pdf"
```

Expected response:
```json
{
  "success": true,
  "files": ["https://crane-intelligence-storage.atl1.digitaloceanspaces.com/prod/service-records/..."],
  "file_urls": ["https://crane-intelligence-storage.atl1.digitaloceanspaces.com/prod/service-records/..."],
  "file_details": [...]
}
```

#### Test Bulk File Upload:

```bash
# Create a test CSV file
echo "col1,col2" > /tmp/test.csv
echo "val1,val2" >> /tmp/test.csv

# Upload via API
curl -X POST http://localhost:8004/api/v1/fmv-reports/upload-bulk-file \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/tmp/test.csv"
```

### Step 5: Verify Files in DigitalOcean Spaces

1. Log into DigitalOcean Spaces dashboard
2. Navigate to bucket: `crane-intelligence-storage`
3. Check folders:
   - `prod/service-records/` - for service record files
   - `prod/bulk-processing/` - for bulk processing files
   - `prod/test-uploads/` - for test files

Files should appear with format: `{uuid}_{original_filename}`

### Step 6: Check Frontend Upload

1. Go to https://craneintelligence.tech/report-generation.html
2. Upload a file (service record or bulk file)
3. Check browser console for upload success messages
4. Verify the file URL is returned and stored in `service_record_files`

### Step 7: Verify Files Display in Dashboard/Admin

1. After creating an FMV report with uploaded files
2. Go to dashboard: https://craneintelligence.tech/dashboard.html
3. Click on the FMV report tile
4. Check "Service Records & Documents" section
5. Files should be displayed with download links

## Troubleshooting

### Issue: Storage service not initialized

**Symptoms:**
- Logs show: `❌ Storage service s3_client is None`
- Upload endpoints return 500 error

**Solutions:**
1. Check `.env` file has `DO_SPACES_KEY` and `DO_SPACES_SECRET`
2. Verify credentials are correct
3. Check backend logs for initialization errors
4. Restart backend after setting environment variables

### Issue: Upload fails with "InvalidAccessKeyId"

**Symptoms:**
- Error: `InvalidAccessKeyId - None`
- Upload returns 500 error

**Solutions:**
1. Verify `DO_SPACES_KEY` is set correctly
2. Check key is not expired in DigitalOcean dashboard
3. Ensure key has proper permissions for the bucket

### Issue: Files not appearing in DigitalOcean Spaces

**Symptoms:**
- Upload returns success but files not in Spaces
- CDN URL is returned but file doesn't exist

**Solutions:**
1. Check backend logs for upload errors
2. Verify bucket name is correct: `crane-intelligence-storage`
3. Check region is correct: `atl1`
4. Verify CDN endpoint format: `https://crane-intelligence-storage.atl1.digitaloceanspaces.com`

### Issue: Files not displayed in dashboard/admin

**Symptoms:**
- Files uploaded successfully
- Files exist in DigitalOcean Spaces
- But not shown in dashboard/admin panel

**Solutions:**
1. Check `service_record_files` field in database
2. Verify URLs are stored correctly (should start with `https://`)
3. Check browser console for JavaScript errors
4. Verify frontend is parsing `service_record_files` correctly

## Log Locations

- Backend logs: Check where uvicorn is logging (usually stdout/stderr or log file)
- If using `start_backend.sh`: Check the output file specified
- If using systemd: Check journalctl: `journalctl -u crane-backend -f`

## Expected Log Messages

### Successful Initialization:
```
✅ DigitalOcean Spaces client initialized successfully:
   Bucket: crane-intelligence-storage
   Region: atl1
   Environment: prod
   Endpoint: https://atl1.digitaloceanspaces.com
   CDN Endpoint: https://crane-intelligence-storage.atl1.digitaloceanspaces.com
```

### Successful Upload:
```
📤 Uploading service record file: test.pdf (1234 bytes)
✅ Successfully uploaded file to Spaces bucket 'crane-intelligence-storage' with key: prod/service-records/abc123_test.pdf
📎 File uploaded to Spaces [prod]:
   Bucket: crane-intelligence-storage
   Region: atl1
   File Key: prod/service-records/abc123_test.pdf
   CDN URL: https://crane-intelligence-storage.atl1.digitaloceanspaces.com/prod/service-records/abc123_test.pdf
✅ Uploaded service record file to CDN: https://crane-intelligence-storage.atl1.digitaloceanspaces.com/prod/service-records/abc123_test.pdf
```

### Error Messages:
```
❌ DigitalOcean Spaces s3_client is not initialized
   Access Key: SET
   Secret Key: SET
   Bucket: crane-intelligence-storage
   Region: atl1
```

## Next Steps After Verification

1. ✅ Backend restarted with new code
2. ✅ Storage service initialized successfully
3. ✅ Test uploads working
4. ✅ Files appearing in DigitalOcean Spaces
5. ✅ Files displayed in dashboard/admin

If all steps pass, the upload system is working correctly!
