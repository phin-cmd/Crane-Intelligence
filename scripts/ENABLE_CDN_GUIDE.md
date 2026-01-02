# Enable CDN for DigitalOcean Spaces Buckets

## ✅ Buckets Created Successfully

The following buckets have been created:
- ✅ `crane-intelligence-storage-dev`
- ✅ `crane-intelligence-storage-uat`
- ✅ `crane-intelligence-storage` (already existed)

## Step-by-Step: Enable CDN

### 1. Access DigitalOcean Dashboard

Go to: **https://cloud.digitalocean.com/spaces**

### 2. Enable CDN for Each Bucket

For each bucket (`crane-intelligence-storage-dev`, `crane-intelligence-storage-uat`, `crane-intelligence-storage`):

1. **Click on the bucket name** to open it
2. **Navigate to the "Settings" tab**
3. **Find "CDN (Content Delivery Network)" section**
4. **Click "Enable CDN"** or toggle it on
5. **Wait for CDN to be provisioned** (usually takes 1-2 minutes)
6. **Note the CDN endpoint** - it should match:
   - Dev: `https://crane-intelligence-storage-dev.atl1.cdn.digitaloceanspaces.com`
   - UAT: `https://crane-intelligence-storage-uat.atl1.cdn.digitaloceanspaces.com`
   - Prod: `https://crane-intelligence-storage.atl1.cdn.digitaloceanspaces.com`

### 3. Set Public Read Access (for CDN to work)

For each bucket:

1. **Go to "Settings" tab**
2. **Find "File Listing" or "Public Access" settings**
3. **Enable "Public File Listing"** or set bucket to allow public read access
4. **Alternatively, set a CORS policy** if needed for web uploads

### 4. Verify CDN Endpoints

After enabling CDN, verify the endpoints match your configuration:

```bash
# Check your configuration
grep DO_SPACES_CDN_ENDPOINT config/dev.env
grep DO_SPACES_CDN_ENDPOINT config/uat.env
grep DO_SPACES_CDN_ENDPOINT config/prod.env.template
```

Expected endpoints:
- Dev: `https://crane-intelligence-storage-dev.atl1.cdn.digitaloceanspaces.com`
- UAT: `https://crane-intelligence-storage-uat.atl1.cdn.digitaloceanspaces.com`
- Prod: `https://crane-intelligence-storage.atl1.cdn.digitaloceanspaces.com`

## Quick Verification

After enabling CDN, you can verify it's working by:

1. Upload a test file to any bucket
2. Access it via the CDN URL
3. Check the response headers - should include CDN-related headers

## Next Steps

Once CDN is enabled for all buckets:

1. **Restart backend services** (if not already done):
   ```bash
   ./scripts/restart-backends-with-env-config.sh
   ```

2. **Test file uploads**:
   ```bash
   ./scripts/test-file-uploads.sh
   ```

3. **Verify files are in correct buckets**:
   - Check DigitalOcean Spaces dashboard
   - Verify folder structure: `{environment}/{folder}/{filename}`

## Troubleshooting

### CDN not working?
- Ensure CDN is enabled in the dashboard
- Wait a few minutes for CDN propagation
- Check that files have public read access
- Verify CDN endpoint matches configuration

### Files not accessible?
- Check bucket permissions (public read access)
- Verify CORS settings if uploading from web
- Check that CDN endpoint is correct

### Uploads failing?
- Verify backend containers are running
- Check environment variables in containers
- Review backend logs for errors

