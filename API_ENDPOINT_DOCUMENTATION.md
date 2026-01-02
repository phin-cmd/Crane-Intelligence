# Server Monitoring API Endpoints

## Required API Endpoints

The server monitoring system requires the following API endpoints to be implemented in your backend:

### 1. GET `/api/v1/admin/server-status`

Returns the current status of all monitored servers.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "overall": "healthy",
  "servers": [
    {
      "server": "production",
      "name": "Production Server",
      "status": "healthy",
      "api_status": "healthy",
      "website_status": "healthy",
      "api_response_time": 45.2,
      "website_response_time": 120.5,
      "api_error": null,
      "website_error": null,
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "server": "uat",
      "name": "UAT Server",
      "status": "degraded",
      "api_status": "healthy",
      "website_status": "unhealthy",
      "api_response_time": 50.1,
      "website_response_time": null,
      "api_error": null,
      "website_error": "HTTP 503",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "server": "dev",
      "name": "Development Server",
      "status": "down",
      "api_status": "down",
      "website_status": "down",
      "api_response_time": null,
      "website_response_time": null,
      "api_error": "Connection timeout",
      "website_error": "Connection refused",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some systems have issues but still partially functional
- `down`: Server is completely down
- `unknown`: Status cannot be determined

### 2. POST `/api/v1/admin/alerts`

Receives server alert data from the monitoring script.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "server": "production",
  "server_name": "Production Server",
  "status": "down",
  "api_status": "down",
  "website_status": "down",
  "api_error": "Connection timeout",
  "website_error": "Connection refused",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alert received and processed"
}
```

This endpoint should:
1. Store the alert in the database
2. Create notifications for all admin users
3. Trigger email notifications (if not already sent by the monitoring script)

### 3. GET `/api/v1/health`

Health check endpoint for each server (dev, UAT, production).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

This endpoint should return a 200 status code when the server is healthy.

## Implementation Notes

1. The monitoring script runs every 60 seconds and checks all configured servers
2. Alerts are only sent when status changes (to avoid spam)
3. The admin dashboard polls the server status endpoint every 30 seconds
4. Email notifications are sent immediately when issues are detected
5. The monitoring script can be run as a systemd service for automatic startup

