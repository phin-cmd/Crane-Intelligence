# Consultation Requests Database Table Schema

## Table Name: `consultation_requests`

This table stores consultation requests submitted by users through the homepage "Get Your Free Consultation" form.

### Table Structure

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT, INDEXED | Unique identifier for each consultation request |
| `name` | VARCHAR(255) | NOT NULL, INDEXED | Full name of the person requesting consultation |
| `email` | VARCHAR(255) | NOT NULL, INDEXED | Email address of the requester |
| `company` | VARCHAR(255) | NULLABLE | Company name (optional) |
| `message` | TEXT | NOT NULL | Message/description of consultation needs |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'new', INDEXED | Current status of the consultation request |
| `admin_notes` | TEXT | NULLABLE | Internal notes added by admin users |
| `contacted_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Timestamp when the requester was first contacted |
| `scheduled_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Timestamp when consultation was scheduled |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Timestamp when consultation was completed |
| `email_sent` | BOOLEAN | NOT NULL, DEFAULT FALSE | Flag indicating if notification email was sent to admins |
| `email_sent_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Timestamp when notification email was sent |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Timestamp when request was created |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Timestamp when record was last updated |

### Status Values

The `status` column can have the following values (defined in `ConsultationStatus` enum):

- `new` - Newly submitted request (default)
- `contacted` - Admin has contacted the requester
- `scheduled` - Consultation has been scheduled
- `completed` - Consultation has been completed
- `cancelled` - Request was cancelled

### Indexes

- Primary Key: `id`
- Index on: `name`, `email`, `status`

### Relationships

- No foreign key relationships (standalone table)

### Example SQL Query

```sql
-- Create table (automatically created by SQLAlchemy)
CREATE TABLE consultation_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    admin_notes TEXT,
    contacted_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    email_sent BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_consultation_requests_name ON consultation_requests(name);
CREATE INDEX idx_consultation_requests_email ON consultation_requests(email);
CREATE INDEX idx_consultation_requests_status ON consultation_requests(status);
```

### Sample Data

```sql
INSERT INTO consultation_requests (
    name, 
    email, 
    company, 
    message, 
    status, 
    email_sent,
    created_at
) VALUES (
    'John Doe',
    'john.doe@example.com',
    'ABC Construction',
    'I need help valuing my fleet of 10 cranes for insurance purposes.',
    'new',
    TRUE,
    NOW()
);
```

### API Endpoints

- `POST /api/v1/consultation/submit` - Submit a new consultation request
- `GET /api/v1/consultation` - Get all consultation requests (admin only)
- `GET /api/v1/consultation/{id}` - Get a specific consultation request (admin only)
- `PATCH /api/v1/consultation/{id}` - Update consultation status/notes (admin only)

### Admin Panel

The consultation requests can be viewed and managed at:
- URL: `/admin/consultations.html`
- Access: Admin users only
- Features:
  - View all consultation requests
  - Filter by status
  - View detailed information
  - Update status
  - Add admin notes

