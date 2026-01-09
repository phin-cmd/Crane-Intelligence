# Email Template Usage Guide for Crane Intelligence

## Overview

This guide provides instructions for using the marketing email templates in the Crane Intelligence platform. All templates are designed to maintain consistent branding, build trust, and comply with email marketing best practices.

## Integration with UnifiedEmailService

### Basic Usage

The marketing email templates integrate seamlessly with the existing `UnifiedEmailService`. Here's how to send a marketing email:

```python
from app.services.email_service_unified import UnifiedEmailService

# Initialize the email service
email_service = UnifiedEmailService(prefer_async=True)

# Prepare template context
context = {
    'user_name': 'John Doe',
    'user_email': 'john@example.com',
    'dashboard_url': 'https://craneintelligence.tech/dashboard.html',
    'support_email': 'phin@accranes.com',
    'unsubscribe_url': 'https://craneintelligence.tech/unsubscribe?token=xxx'
}

# Send marketing email
result = await email_service.send_template_email(
    to_emails=['john@example.com'],
    template_name='marketing/welcome_series_1.html',
    template_context=context,
    subject='Welcome to Crane Intelligence!'
)
```

### Sync vs Async

**Async (Recommended):**
```python
result = await email_service.send_email_async(
    recipients=['user@example.com'],
    subject='Welcome to Crane Intelligence',
    template_name='marketing/welcome_series_1.html',
    context=context
)
```

**Sync:**
```python
result = email_service.send_template_email(
    to_emails=['user@example.com'],
    template_name='marketing/welcome_series_1.html',
    template_context=context,
    subject='Welcome to Crane Intelligence!'
)
```

## Template Variable Reference

### Standard Variables (Available in All Templates)

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `user_name` | string | Recipient's name | "John Doe" |
| `user_email` | string | Recipient's email address | "john@example.com" |
| `company_name` | string | Company name (B2B context) | "ABC Construction" |
| `support_email` | string | Support email address | "phin@accranes.com" |
| `company_address` | string | Physical business address | "4420 W Grace St, Richmond, VA 23230-3808" |
| `company_phone` | string | Phone number | "+1 (434) 531-7566" |
| `unsubscribe_url` | string | Unsubscribe link (required for marketing) | "https://craneintelligence.tech/unsubscribe?token=xxx" |
| `logo_url` | string | Logo image URL (fallback) | "https://craneintelligence.tech/images/logos/crane-intelligence-logo-white.svg" |

### Template-Specific Variables

#### Welcome Series Email (`welcome_series_1.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `dashboard_url` | string | Link to user dashboard | Recommended |
| `support_email` | string | Support email | Recommended |

#### Newsletter Template (`newsletter_template.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `newsletter_title` | string | Newsletter title | Recommended |
| `newsletter_date` | string | Publication date | Optional |
| `articles` | list | List of article objects | Optional |
| `unsubscribe_url` | string | Unsubscribe link | **Required** |

**Article Object Structure:**
```python
articles = [
    {
        'title': 'Article Title',
        'excerpt': 'Article excerpt...',
        'url': 'https://craneintelligence.tech/article/1'
    }
]
```

#### Promotional Announcement (`promotional_announcement.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `announcement_title` | string | Main announcement title | Recommended |
| `hero_message` | string | Hero section message | Optional |
| `announcement_body` | string | Main announcement content | Recommended |
| `offer_details` | string | Special offer description | Optional |
| `cta_url` | string | Primary CTA link | Recommended |
| `cta_text` | string | Primary CTA button text | Optional |
| `secondary_cta_url` | string | Secondary CTA link | Optional |
| `secondary_cta_text` | string | Secondary CTA button text | Optional |
| `expiry_date` | string | Offer expiration date | Optional |
| `benefit_1`, `benefit_2`, `benefit_3` | string | Key benefits | Optional |

#### Feature Update (`feature_update.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `feature_name` | string | Name of the new feature | Recommended |
| `feature_description` | string | Feature description | Recommended |
| `feature_url` | string | Link to feature page | Recommended |
| `release_date` | string | Release date | Optional |
| `benefit_1`, `benefit_2`, `benefit_3` | string | Feature benefits | Optional |

#### Case Study Showcase (`case_study_showcase.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `customer_name` | string | Customer's name | Recommended |
| `company_name` | string | Customer's company | Recommended |
| `testimonial` | string | Customer testimonial quote | Recommended |
| `results` | string | HTML content with results/metrics | Optional |
| `case_study_url` | string | Link to full case study | Recommended |

#### Event Invitation (`event_invitation.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `event_name` | string | Event name | **Required** |
| `event_date` | string | Event date | **Required** |
| `event_time` | string | Event time | **Required** |
| `event_location` | string | Event location (if in-person) | Optional |
| `event_description` | string | Event description | Optional |
| `registration_url` | string | Registration link | **Required** |
| `calendar_link` | string | Add to calendar link | Optional |
| `expectation_1`, `expectation_2`, `expectation_3` | string | What to expect | Optional |

#### Re-engagement Campaign (`re_engagement.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `last_login_date` | string | Last login date | Recommended |
| `special_offer` | string | Special welcome back offer | Optional |
| `dashboard_url` | string | Link to dashboard | Recommended |
| `update_1`, `update_2`, `update_3` | string | Recent platform updates | Optional |

#### Seasonal Promotion (`seasonal_promotion.html`)

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `promotion_title` | string | Promotion title | Recommended |
| `seasonal_message` | string | Seasonal greeting/message | Optional |
| `promotion_description` | string | Promotion description | Recommended |
| `discount_code` | string | Discount/promo code | Optional |
| `offer_details` | string | Offer details | Recommended |
| `expiry_date` | string | Promotion expiration | Recommended |
| `promotion_url` | string | Link to promotion page | Recommended |
| `cta_text` | string | CTA button text | Optional |
| `benefit_1`, `benefit_2`, `benefit_3` | string | Promotion benefits | Optional |

## Best Practices for Personalization

### 1. Always Include User Name

```python
context = {
    'user_name': user.first_name or user.full_name or 'there',
    # ... other variables
}
```

### 2. Use Default Values

All templates use Jinja2's `default` filter to provide fallbacks:

```python
{{ user_name|default('there') }}
{{ dashboard_url|default('https://craneintelligence.tech/dashboard.html') }}
```

### 3. Conditional Content

Use Jinja2 conditionals for optional content:

```python
{% if special_offer %}
<div class="special-offer">
    {{ special_offer }}
</div>
{% endif %}
```

### 4. Dynamic Lists

For newsletter articles or feature lists:

```python
context = {
    'articles': [
        {'title': 'Title 1', 'excerpt': '...', 'url': '...'},
        {'title': 'Title 2', 'excerpt': '...', 'url': '...'}
    ]
}
```

## A/B Testing Guidelines

### Subject Line Testing

Test different subject lines to optimize open rates:

```python
subjects = [
    'Welcome to Crane Intelligence!',
    'Your Crane Intelligence account is ready',
    'Get started with professional crane valuations'
]

# Send to different segments
for i, subject in enumerate(subjects):
    segment = users[i::len(subjects)]  # Split users into groups
    send_email(segment, subject)
```

### CTA Testing

Test different CTA button colors and text:

- Primary: Green (#00FF85) - "Get Started"
- Secondary: Yellow (#FFD600) - "Learn More"

### Content Testing

Test different content approaches:
- Short vs. long emails
- Single vs. multiple CTAs
- With vs. without images

## Compliance Requirements

### CAN-SPAM Act (US)

**Required Elements:**
1. ✅ Physical mailing address in footer
2. ✅ Clear unsubscribe mechanism
3. ✅ Accurate sender information
4. ✅ Honor unsubscribe requests within 10 business days

**Implementation:**
```python
context = {
    'unsubscribe_url': f'https://craneintelligence.tech/unsubscribe?token={unsubscribe_token}',
    # Footer automatically includes physical address
}
```

### GDPR (EU)

**Requirements:**
1. ✅ Explicit consent for marketing emails
2. ✅ Easy unsubscribe process
3. ✅ Privacy policy link
4. ✅ Data processing transparency

**Implementation:**
- Always check user consent before sending
- Provide one-click unsubscribe
- Include privacy policy link in footer

### Unsubscribe Implementation

```python
# Generate unsubscribe token
unsubscribe_token = generate_secure_token(user.id)

# Include in email context
context = {
    'unsubscribe_url': f'https://craneintelligence.tech/unsubscribe?token={unsubscribe_token}'
}

# Handle unsubscribe request
@app.post('/unsubscribe')
async def unsubscribe(token: str):
    user = verify_unsubscribe_token(token)
    user.marketing_emails_enabled = False
    db.commit()
    return {'message': 'Successfully unsubscribed'}
```

## Analytics and Tracking

### Email Open Tracking

Most email services (Brevo, SendGrid) provide built-in tracking. For custom tracking:

```python
# Add tracking pixel to templates
<img src="https://craneintelligence.tech/api/track/email-open?email={{ user_email|urlencode }}&campaign={{ campaign_id }}" 
     width="1" height="1" style="display: none;" />
```

### Click Tracking

Track CTA clicks:

```python
# Wrap links with tracking
tracking_url = f'https://craneintelligence.tech/api/track/click?url={encoded_url}&email={user_email}&campaign={campaign_id}'
context = {
    'cta_url': tracking_url
}
```

### Campaign Tracking

```python
context = {
    'campaign_id': 'welcome-series-2025-01',
    'utm_source': 'email',
    'utm_medium': 'marketing',
    'utm_campaign': 'welcome-series'
}
```

## Example Implementations

### Sending Welcome Email

```python
async def send_welcome_email(user: User):
    email_service = UnifiedEmailService(prefer_async=True)
    
    context = {
        'user_name': user.first_name or user.full_name,
        'user_email': user.email,
        'dashboard_url': f'https://craneintelligence.tech/dashboard.html?user={user.id}',
        'support_email': 'phin@accranes.com',
        'unsubscribe_url': generate_unsubscribe_url(user)
    }
    
    result = await email_service.send_email_async(
        recipients=[user.email],
        subject='Welcome to Crane Intelligence!',
        template_name='marketing/welcome_series_1.html',
        context=context
    )
    
    return result
```

### Sending Newsletter

```python
async def send_newsletter(subscribers: List[User], articles: List[dict]):
    email_service = UnifiedEmailService(prefer_async=True)
    
    for subscriber in subscribers:
        context = {
            'user_name': subscriber.first_name,
            'user_email': subscriber.email,
            'newsletter_title': 'Crane Intelligence Monthly Newsletter',
            'newsletter_date': datetime.now().strftime('%B %Y'),
            'articles': articles,
            'unsubscribe_url': generate_unsubscribe_url(subscriber)
        }
        
        await email_service.send_email_async(
            recipients=[subscriber.email],
            subject='Crane Intelligence Newsletter - ' + datetime.now().strftime('%B %Y'),
            template_name='marketing/newsletter_template.html',
            context=context
        )
```

### Sending Promotional Email

```python
async def send_promotion(users: List[User], promotion_data: dict):
    email_service = UnifiedEmailService(prefer_async=True)
    
    for user in users:
        context = {
            'user_name': user.first_name,
            'user_email': user.email,
            'announcement_title': promotion_data['title'],
            'announcement_body': promotion_data['body'],
            'offer_details': promotion_data.get('offer'),
            'cta_url': promotion_data['cta_url'],
            'cta_text': promotion_data.get('cta_text', 'Learn More'),
            'expiry_date': promotion_data.get('expiry'),
            'unsubscribe_url': generate_unsubscribe_url(user)
        }
        
        await email_service.send_email_async(
            recipients=[user.email],
            subject=promotion_data['title'],
            template_name='marketing/promotional_announcement.html',
            context=context
        )
```

## Error Handling

### Template Rendering Errors

```python
try:
    result = await email_service.send_email_async(...)
    if not result.get('success'):
        logger.error(f"Failed to send email: {result.get('message')}")
except Exception as e:
    logger.error(f"Error sending email: {e}", exc_info=True)
    # Fallback: Send plain text email or log for manual follow-up
```

### Missing Variables

Templates use default values, but best practice is to provide all variables:

```python
# Good: Provide all variables
context = {
    'user_name': user.name,
    'user_email': user.email,
    'dashboard_url': dashboard_url,
    # ... all other variables
}

# Acceptable: Use defaults (templates handle this)
context = {
    'user_email': user.email
    # Other variables will use defaults
}
```

## Testing

### Preview Templates

Before sending, preview templates with sample data:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('backend/templates/emails'))
template = env.get_template('marketing/welcome_series_1.html')

html = template.render(
    user_name='Test User',
    user_email='test@example.com',
    dashboard_url='https://craneintelligence.tech/dashboard.html'
)

# Save to file for preview
with open('preview.html', 'w') as f:
    f.write(html)
```

### Email Client Testing

Test emails in:
- Gmail (web, iOS, Android)
- Outlook (2016, 2019, 365)
- Apple Mail (macOS, iOS)
- Yahoo Mail
- Mobile clients

Use tools like Litmus or Email on Acid for comprehensive testing.

## Troubleshooting

### Images Not Displaying

- Ensure logo URL is accessible
- Check image dimensions and file sizes
- Verify alt text is present
- Test with images disabled

### Styling Issues

- Most styles are inline for compatibility
- Test in Outlook (most restrictive)
- Use table-based layouts
- Avoid advanced CSS

### Unsubscribe Link Not Working

- Verify token generation
- Check URL encoding
- Test unsubscribe endpoint
- Ensure proper error handling

## Support

For questions or issues:
- Email: phin@accranes.com
- Phone: +1 (434) 531-7566
- Documentation: See EMAIL_BRAND_GUIDE.md and EMAIL_DESIGN_SPECS.md

## Revision History

- **2025-01-XX**: Initial usage guide created

---

**Related Documentation:**
- [EMAIL_BRAND_GUIDE.md](EMAIL_BRAND_GUIDE.md) - Brand guidelines and standards
- [EMAIL_DESIGN_SPECS.md](EMAIL_DESIGN_SPECS.md) - Design specifications and components
