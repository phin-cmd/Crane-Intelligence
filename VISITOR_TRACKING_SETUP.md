# Visitor Tracking Setup Guide

## Overview
The visitor tracking system has been successfully integrated into the Crane Intelligence platform. This system tracks website visitors, demographics, and behavior analytics.

## What Has Been Implemented

### 1. Database Model
- **File**: `/root/crane/backend/app/models/visitor_tracking.py`
- **Table**: `visitor_tracking`
- Tracks: visitors, sessions, page views, device info, location, engagement metrics, traffic sources

### 2. Backend API Endpoints
- **File**: `/root/crane/backend/app/api/v1/visitor_tracking.py`
- **Router**: `/api/v1/visitor-tracking`
- **Endpoints**:
  - `POST /track` - Track page views (public, no auth required)
  - `PUT /update/{id}` - Update engagement metrics
  - `GET /stats` - Get visitor statistics (admin only)
  - `GET /demographics` - Get demographics data (admin only)
  - `GET /timeline` - Get timeline data for charts (admin only)
  - `GET /pages` - Get top pages (admin only)

### 3. Frontend Tracking Script
- **File**: `/root/crane/js/visitor-tracker.js`
- Automatically tracks page views, scroll depth, time on page
- Uses cookies for visitor/session identification
- Included on:
  - `homepage.html`
  - `dashboard.html`
  - `report-generation.html`

### 4. Analytics Dashboard
- **File**: `/root/crane/admin/analytics.html`
- Integrated with admin layout system
- Displays:
  - Visitor statistics (total visitors, page views, sessions, bounce rate, avg time)
  - Visitor timeline chart
  - Demographics charts (countries, devices, browsers, OS, traffic sources)
  - Top pages table

## Database Setup

The `visitor_tracking` table will be automatically created when the application starts, as the model has been added to the database initialization in `/root/crane/backend/app/core/database.py`.

### Manual Migration (if needed)
If you need to manually create the table, you can run:

```bash
cd /root/crane/backend
python migrations/create_visitor_tracking_table.py
```

Or restart the backend server - the table will be created automatically via `Base.metadata.create_all()`.

## How It Works

1. **Tracking**: When a user visits any page with the tracking script:
   - A unique visitor ID is stored in a cookie (1 year expiry)
   - A session ID is stored in a cookie (30 minutes expiry)
   - Page view data is sent to `/api/v1/visitor-tracking/track`
   - Device, browser, OS, and location data is automatically detected

2. **Engagement Tracking**:
   - Scroll depth is tracked as the user scrolls
   - Time on page is updated every 30 seconds
   - Final metrics are sent on page unload

3. **Analytics Dashboard**:
   - Admin users can view comprehensive analytics at `/admin/analytics.html`
   - Data is automatically loaded when the page is accessed
   - Charts and tables update based on selected time range

## Testing

1. **Test Tracking**:
   - Visit any page with the tracking script (homepage, dashboard, etc.)
   - Check browser console for tracking logs (if debug mode enabled)
   - Verify cookies are set: `visitor_id` and `session_id`

2. **Test Analytics Dashboard**:
   - Log in as admin user
   - Navigate to `/admin/analytics.html`
   - Verify visitor statistics are displayed
   - Check that charts render correctly

3. **Test API Endpoints**:
   ```bash
   # Track a page view (no auth required)
   curl -X POST https://craneintelligence.tech/api/v1/visitor-tracking/track \
     -H "Content-Type: application/json" \
     -d '{"page_url": "https://craneintelligence.tech/", "page_title": "Home"}'
   
   # Get stats (requires admin token)
   curl -X GET "https://craneintelligence.tech/api/v1/visitor-tracking/stats?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59" \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
   ```

## Privacy Considerations

- Visitor tracking uses cookies to identify unique visitors
- IP addresses are stored but can be anonymized if needed
- No personally identifiable information is collected unless the user is logged in
- All tracking respects browser privacy settings (Do Not Track, etc.)

## Next Steps

1. **Restart Backend Server**: The table will be created automatically
2. **Verify Tracking**: Visit pages and check that data is being collected
3. **View Analytics**: Access the admin analytics dashboard to see the data
4. **Optional Enhancements**:
   - Add IP geolocation service for more accurate location data
   - Implement bot detection to filter out crawlers
   - Add custom event tracking for specific user actions
   - Export analytics data to CSV/JSON

## Troubleshooting

### Table Not Created
- Check backend logs for errors
- Verify the model is imported in `database.py`
- Run the migration script manually

### Tracking Not Working
- Check browser console for JavaScript errors
- Verify the tracking script is included in the HTML
- Check network tab for API calls to `/visitor-tracking/track`
- Verify CORS settings allow the tracking endpoint

### Analytics Not Loading
- Verify admin authentication token is valid
- Check browser console for API errors
- Verify the API endpoints are accessible
- Check that data exists in the database

## Support

For issues or questions, check:
- Backend logs: `/root/crane/backend/logs/`
- Browser console for frontend errors
- Network tab for API call failures

