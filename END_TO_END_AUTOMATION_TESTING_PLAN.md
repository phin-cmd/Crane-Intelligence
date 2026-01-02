# End-to-End Automation Testing Plan
## Crane Intelligence Platform - Comprehensive Test Coverage

**Version:** 3.0  
**Last Updated:** December 2024  
**Comprehensive Update:** Based on complete platform analysis and all existing features  
**Platform:** https://dev.craneintelligence.tech/  
**Test Framework:** Playwright / Cypress / Selenium (Recommended: Playwright)

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Authentication & User Management](#authentication--user-management)
3. [Public Website Features](#public-website-features)
4. [User Dashboard & Core Features](#user-dashboard--core-features)
5. [Valuation Terminal](#valuation-terminal)
6. [FMV Report Generation & Management](#fmv-report-generation--management)
7. [Payment Processing](#payment-processing)
8. [Admin Panel - Complete Coverage](#admin-panel---complete-coverage)
9. [Equipment Management](#equipment-management)
10. [API Endpoint Testing](#api-endpoint-testing)
11. [Notification Preferences](#notification-preferences)
12. [Email & Notifications](#email--notifications)
13. [Data Management & Analytics](#data-management--analytics)
14. [Security & Compliance](#security--compliance)
15. [Performance & Load Testing](#performance--load-testing)
16. [Cross-Browser & Responsive Testing](#cross-browser--responsive-testing)
17. [Error Handling & Edge Cases](#error-handling--edge-cases)
18. [Integration & End-to-End Workflows](#integration--end-to-end-workflows)

---

## 1. Test Environment Setup

### 1.1 Pre-requisites
- [ ] Set up test database (separate from production)
- [ ] Configure test environment variables
- [ ] Set up test Stripe account (test mode)
- [ ] Configure test email service (Brevo test account)
- [ ] Initialize test data (users, reports, equipment)
- [ ] Set up test admin credentials
- [ ] Configure API test endpoints

### 1.2 Test Data Management
- [ ] Create test user accounts (various roles)
- [ ] Create test admin accounts
- [ ] Seed test equipment/crane data
- [ ] Create test FMV reports (various statuses)
- [ ] Set up test payment methods
- [ ] Create test notifications

---

## 2. Authentication & User Management

### 2.1 User Registration
- [ ] **TC-AUTH-001**: Register new user with valid credentials
  - Navigate to homepage
  - Click "Sign Up" button
  - Fill registration form (First Name, Last Name, Email, Password, Confirm Password, Role)
  - Select role from dropdown (Crane Rental Company, Equipment Dealer, Financial Institution, Other)
  - Submit form
  - Verify email verification message displayed
  - Verify redirect to email verification page
  - Check email inbox for verification email
  - Verify user created in database

- [ ] **TC-AUTH-002**: Registration with invalid email format
  - Attempt registration with invalid email (e.g., "invalid-email")
  - Verify error message displayed
  - Verify form not submitted

- [ ] **TC-AUTH-003**: Registration with weak password
  - Attempt registration with password < 8 characters
  - Verify password strength validation
  - Verify form not submitted

- [ ] **TC-AUTH-004**: Registration with mismatched passwords
  - Enter different passwords in Password and Confirm Password fields
  - Verify error message displayed
  - Verify form not submitted

- [ ] **TC-AUTH-005**: Registration with existing email
  - Attempt registration with email already in system
  - Verify error message displayed
  - Verify user not created

- [ ] **TC-AUTH-006**: Registration with missing required fields
  - Attempt registration leaving required fields empty
  - Verify field-level validation errors
  - Verify form not submitted

### 2.2 Email Verification
- [ ] **TC-AUTH-007**: Email verification with valid token
  - Receive verification email
  - Click verification link
  - Verify email verified in database
  - Verify redirect to login page
  - Verify success message displayed

- [ ] **TC-AUTH-008**: Email verification with invalid/expired token
  - Attempt verification with invalid token
  - Verify error message displayed
  - Verify user remains unverified

- [ ] **TC-AUTH-009**: Resend verification email
  - Navigate to resend verification page
  - Enter email address
  - Submit form
  - Verify new verification email sent
  - Verify success message displayed

### 2.3 User Login
- [ ] **TC-AUTH-010**: Login with valid credentials
  - Navigate to homepage
  - Click "Login" button
  - Enter valid email and password
  - Click "Sign In"
  - Verify successful login
  - Verify redirect to dashboard
  - Verify user session created
  - Verify JWT token stored in localStorage

- [ ] **TC-AUTH-011**: Login with invalid email
  - Attempt login with non-existent email
  - Verify error message displayed
  - Verify no session created

- [ ] **TC-AUTH-012**: Login with incorrect password
  - Attempt login with correct email but wrong password
  - Verify error message displayed
  - Verify no session created

- [ ] **TC-AUTH-013**: Login with unverified email
  - Attempt login with unverified account
  - Verify error message prompting verification
  - Verify redirect to verification page

- [ ] **TC-AUTH-014**: Login with empty fields
  - Attempt login leaving email/password empty
  - Verify field validation errors
  - Verify form not submitted

- [ ] **TC-AUTH-015**: Remember me functionality
  - Login with "Remember me" checked
  - Close browser
  - Reopen browser and navigate to site
  - Verify user still logged in

### 2.4 Password Reset
- [ ] **TC-AUTH-016**: Request password reset
  - Navigate to login page
  - Click "Forgot Password?" link
  - Enter registered email address
  - Submit form
  - Verify reset email sent
  - Verify success message displayed

- [ ] **TC-AUTH-017**: Password reset with invalid email
  - Attempt password reset with non-existent email
  - Verify error message displayed

- [ ] **TC-AUTH-018**: Reset password with valid token
  - Receive password reset email
  - Click reset link
  - Enter new password
  - Confirm new password
  - Submit form
  - Verify password updated in database
  - Verify redirect to login page
  - Verify login with new password works

- [ ] **TC-AUTH-019**: Reset password with invalid/expired token
  - Attempt reset with invalid token
  - Verify error message displayed
  - Verify password not changed

- [ ] **TC-AUTH-020**: Reset password with weak password
  - Attempt reset with password < 8 characters
  - Verify validation error
  - Verify password not changed

### 2.5 User Profile Management
- [ ] **TC-AUTH-021**: View user profile
  - Login as user
  - Navigate to Account Settings
  - Verify profile information displayed correctly
  - Verify all fields populated

- [ ] **TC-AUTH-022**: Update user profile
  - Navigate to Account Settings
  - Update First Name, Last Name, Company Name
  - Save changes
  - Verify success message
  - Verify changes saved in database
  - Verify changes reflected on page

- [ ] **TC-AUTH-023**: Change email address
  - Navigate to Account Settings
  - Update email address
  - Save changes
  - Verify email verification required
  - Verify old email receives notification
  - Verify new email receives verification email

- [ ] **TC-AUTH-024**: Change password
  - Navigate to Account Settings
  - Enter current password
  - Enter new password
  - Confirm new password
  - Save changes
  - Verify password updated
  - Verify email notification sent
  - Verify logout and login with new password

- [ ] **TC-AUTH-025**: Logout
  - Login as user
  - Click logout button
  - Verify session terminated
  - Verify redirect to homepage
  - Verify JWT token removed from localStorage
  - Verify cannot access protected pages

---

## 3. Public Website Features

### 3.1 Homepage Navigation
- [ ] **TC-PUBLIC-001**: Homepage loads correctly
  - Navigate to homepage
  - Verify page loads without errors
  - Verify all sections visible
  - Verify navigation menu present
  - Verify footer present

- [ ] **TC-PUBLIC-002**: Navigation menu links
  - Click "FEATURES" link
  - Verify navigation to features section
  - Click "PRICING" link
  - Verify navigation to pricing section
  - Click "ABOUT" link
  - Verify navigation to about section
  - Click "CONTACT" link
  - Verify navigation to contact section

- [ ] **TC-PUBLIC-003**: Logo click redirects to homepage
  - Navigate to any page
  - Click logo
  - Verify redirect to homepage

- [ ] **TC-PUBLIC-004**: Footer links functionality
  - Scroll to footer
  - Click "About Us" link
  - Verify navigation to about page
  - Click "Contact" link
  - Verify navigation to contact page
  - Click "Blog" link
  - Verify navigation to blog page
  - Click "Privacy Policy" link
  - Verify navigation to privacy policy page
  - Click "Terms of Service" link
  - Verify navigation to terms page
  - Click "Cookie Policy" link
  - Verify navigation to cookie policy page
  - Click "Security" link
  - Verify navigation to security page

### 3.2 Pricing Section
- [ ] **TC-PUBLIC-005**: View pricing tiers
  - Navigate to pricing section
  - Verify all three tiers displayed:
    - Spot Check — $250
    - Professional — $995
    - Fleet Valuation — from $1,495
  - Verify features listed for each tier
  - Verify pricing information accurate

- [ ] **TC-PUBLIC-006**: Select Spot Check pricing tier
  - Click "Get Spot Check" or "Submit Request" button
  - Verify redirect to appropriate page/form
  - Verify pricing tier selected

- [ ] **TC-PUBLIC-007**: Select Professional pricing tier
  - Click "Select Professional" or "Submit Request" button
  - Verify redirect to appropriate page/form
  - Verify pricing tier selected

- [ ] **TC-PUBLIC-008**: Select Fleet Valuation pricing tier
  - Click "Select Fleet" or "Submit Fleet Request" button
  - Verify redirect to appropriate page/form
  - Verify pricing tier selected

### 3.3 Consultation Form
- [ ] **TC-PUBLIC-009**: Submit consultation form
  - Navigate to consultation section
  - Fill form fields:
    - Your Name
    - Email Address
    - Company Name
    - Message/Needs description
  - Click "Schedule Free Consultation"
  - Verify form submission
  - Verify success message displayed
  - Verify email notification sent
  - Verify consultation record created in database

- [ ] **TC-PUBLIC-010**: Consultation form validation
  - Attempt submission with empty fields
  - Verify field-level validation errors
  - Attempt submission with invalid email
  - Verify email validation error
  - Verify form not submitted

### 3.4 Newsletter Subscription
- [ ] **TC-PUBLIC-011**: Subscribe to newsletter
  - Scroll to footer
  - Enter email in newsletter subscription field
  - Click "SUBSCRIBE" button
  - Verify subscription success message
  - Verify email added to newsletter list
  - Verify confirmation email sent

- [ ] **TC-PUBLIC-012**: Newsletter subscription validation
  - Attempt subscription with invalid email
  - Verify validation error
  - Attempt subscription with empty email
  - Verify validation error

### 3.5 Static Pages
- [ ] **TC-PUBLIC-013**: About Us page
  - Navigate to About Us page
  - Verify page loads correctly
  - Verify content displayed
  - Verify no broken links

- [ ] **TC-PUBLIC-014**: Contact page
  - Navigate to Contact page
  - Verify contact form present
  - Verify contact information displayed
  - Submit contact form
  - Verify form submission works

- [ ] **TC-PUBLIC-015**: Blog page
  - Navigate to Blog page
  - Verify blog posts displayed
  - Click on blog post
  - Verify post details page loads

- [ ] **TC-PUBLIC-016**: Legal pages (Privacy Policy, Terms, Cookie Policy, Security)
  - Navigate to each legal page
  - Verify page loads correctly
  - Verify content displayed
  - Verify no broken links

---

## 4. User Dashboard & Core Features

### 4.1 Dashboard Access
- [ ] **TC-DASH-001**: Access dashboard after login
  - Login as user
  - Verify redirect to dashboard
  - Verify dashboard loads correctly
  - Verify user information displayed

- [ ] **TC-DASH-002**: Dashboard without authentication
  - Attempt to access dashboard URL directly without login
  - Verify redirect to login page
  - Verify error message displayed

### 4.2 Dashboard Statistics
- [ ] **TC-DASH-003**: View dashboard statistics
  - Login and navigate to dashboard
  - Verify statistics displayed:
    - Total Valuations
    - Active Reports
    - Total Spent
    - Recent Activity
  - Verify statistics are accurate
  - Verify statistics update in real-time

- [ ] **TC-DASH-004**: Dashboard charts and graphs
  - Verify charts load correctly
  - Verify chart data accurate
  - Verify chart interactions work
  - Verify chart responsiveness

### 4.3 Dashboard Navigation
- [ ] **TC-DASH-005**: Navigate to FMV Reports
  - Click "FMV Report" link in header
  - Verify navigation to FMV reports page
  - Verify page loads correctly

- [ ] **TC-DASH-006**: Navigate to Account Settings
  - Click "Account Setting" link in header
  - Verify navigation to account settings page
  - Verify page loads correctly

- [ ] **TC-DASH-007**: Access notifications
  - Click notifications bell icon
  - Verify notifications dropdown opens
  - Verify notifications displayed
  - Click "View all notification"
  - Verify navigation to notifications page

- [ ] **TC-DASH-008**: Mark notifications as read
  - Open notifications dropdown
  - Click "Mark all as read"
  - Verify notifications marked as read
  - Verify UI updates

### 4.4 My Reports Page
- [ ] **TC-DASH-009**: View user's FMV reports
  - Navigate to "My Reports" or "FMV Reports" page
  - Verify all user's reports displayed
  - Verify report status shown correctly
  - Verify report details visible (date, type, status, price)

- [ ] **TC-DASH-010**: Filter reports by status
  - Navigate to reports page
  - Apply status filter (Pending, In Progress, Completed, etc.)
  - Verify filtered results displayed
  - Verify filter works correctly

- [ ] **TC-DASH-011**: Search reports
  - Navigate to reports page
  - Enter search term
  - Verify search results displayed
  - Verify search works correctly

- [ ] **TC-DASH-012**: View report details
  - Click on a report
  - Verify report details page loads
  - Verify all report information displayed
  - Verify timeline/history visible

- [ ] **TC-DASH-013**: Download completed report PDF
  - Navigate to completed report
  - Click download button
  - Verify PDF downloads
  - Verify PDF content correct

- [ ] **TC-DASH-014**: View report receipt
  - Navigate to paid report
  - Click "View Receipt" or similar
  - Verify receipt displayed
  - Verify receipt information accurate

---

## 5. Valuation Terminal

### 5.1 Valuation Terminal Access
- [ ] **TC-VAL-001**: Access valuation terminal
  - Login as user
  - Navigate to Valuation Terminal
  - Verify terminal loads correctly
  - Verify all sections visible
  - Verify market ticker displayed
  - Verify live data updates

- [ ] **TC-VAL-002**: Valuation terminal without authentication
  - Attempt to access terminal without login
  - Verify redirect to login page
  - Verify error message displayed

### 5.2 Crane Valuation Input
- [ ] **TC-VAL-003**: Enter crane specifications
  - Navigate to valuation terminal
  - Fill in crane details:
    - Manufacturer (from dropdown)
    - Model (from dropdown)
    - Year
    - Capacity
    - Hours/Mileage
    - Condition
    - Location/Region
    - Serial Number
    - Additional specifications
  - Verify all fields accept input
  - Verify field validation works
  - Verify real-time validation feedback

- [ ] **TC-VAL-004**: Select manufacturer and model
  - Select manufacturer from dropdown
  - Verify model dropdown populated dynamically
  - Verify model dropdown filtered by manufacturer
  - Select model from dropdown
  - Verify model details loaded automatically
  - Verify model specifications pre-filled if available

- [ ] **TC-VAL-005**: Input validation
  - Attempt to submit with missing required fields
  - Verify validation errors displayed
  - Verify field-level error messages
  - Enter invalid year (future year, negative, before 1900)
  - Verify validation error with helpful message
  - Enter invalid capacity (negative, zero, extremely large)
  - Verify validation error
  - Enter invalid hours/mileage (negative)
  - Verify validation error
  - Enter special characters in text fields
  - Verify proper sanitization

### 5.3 Standard Valuation Calculation
- [ ] **TC-VAL-006**: Calculate standard crane valuation
  - Enter complete crane specifications
  - Click "Calculate Valuation" or "Get Valuation"
  - Verify calculation initiated
  - Verify loading indicator shown
  - Verify progress updates displayed
  - Verify valuation results displayed
  - Verify valuation amount shown (FMV range)
  - Verify confidence score displayed
  - Verify calculation time displayed

- [ ] **TC-VAL-007**: Valuation results display
  - After calculation, verify:
    - Estimated FMV range displayed (low, high, average)
    - Comparable sales shown with details
    - Market analysis displayed
    - Risk assessment shown
    - Regional commentary displayed
    - Deal Score calculated and displayed
    - Wear Score calculated and displayed
    - Market trends visible
  - Verify all data accurate
  - Verify data formatted correctly
  - Verify charts/graphs rendered

- [ ] **TC-VAL-008**: Market analysis display
  - Verify market trends displayed
  - Verify comparable equipment shown with details
  - Verify pricing trends visible in charts
  - Verify regional data displayed
  - Verify market conditions commentary
  - Verify supply/demand indicators

- [ ] **TC-VAL-009**: Deal & Wear Score calculation
  - Verify Deal Score calculated (0-100)
  - Verify Wear Score calculated (0-100)
  - Verify scores displayed correctly
  - Verify score explanations shown
  - Verify score breakdown visible
  - Verify score impact on valuation explained

### 5.4 Enhanced Valuation Features
- [ ] **TC-VAL-010**: Enhanced valuation calculation
  - Navigate to enhanced valuation option
  - Enter detailed crane specifications
  - Upload service records (optional)
  - Submit enhanced valuation request
  - Verify enhanced calculation initiated
  - Verify more detailed results displayed
  - Verify additional analysis provided
  - Verify enhanced confidence metrics

- [ ] **TC-VAL-011**: Fleet optimization
  - Navigate to fleet optimization feature
  - Enter multiple cranes (via form or CSV upload)
  - Configure optimization parameters
  - Run fleet analysis
  - Verify fleet optimization results displayed
  - Verify recommendations displayed
  - Verify fleet value summary
  - Verify individual crane recommendations
  - Verify optimization metrics calculated
  - Verify export options available

- [ ] **TC-VAL-012**: Market analysis feature
  - Navigate to market analysis feature
  - Select region/parameters
  - Select equipment type/category
  - Select date range
  - Run analysis
  - Verify market analysis results displayed
  - Verify charts/graphs displayed
  - Verify trend analysis shown
  - Verify pricing insights provided
  - Verify export functionality works

- [ ] **TC-VAL-013**: Real-time market data integration
  - Verify market ticker displays live data
  - Verify ticker updates automatically
  - Verify market data accurate
  - Verify data refresh works
  - Verify no flickering during updates

### 5.5 Valuation Export & Sharing
- [ ] **TC-VAL-014**: Export valuation results
  - Complete valuation
  - Click export button
  - Select export format (PDF, Excel, CSV, JSON)
  - Verify file downloads
  - Verify file content correct
  - Verify file format valid
  - Verify all data included in export

- [ ] **TC-VAL-015**: Share valuation results
  - Complete valuation
  - Click share button
  - Verify share options displayed
  - Test email sharing
  - Test link generation
  - Verify shared link works

### 5.6 Valuation History & Management
- [ ] **TC-VAL-016**: View valuation history
  - Navigate to valuation history
  - Verify past valuations displayed
  - Verify valuation details visible
  - Verify can view previous valuations
  - Verify history sorted by date
  - Verify search/filter functionality

- [ ] **TC-VAL-017**: Save valuation
  - Complete valuation
  - Click "Save" button
  - Verify valuation saved
  - Verify appears in history
  - Verify can reload saved valuation
  - Verify saved data persists

- [ ] **TC-VAL-018**: Delete saved valuation
  - Navigate to saved valuation
  - Click delete button
  - Confirm deletion
  - Verify valuation removed from history
  - Verify cannot access deleted valuation

- [ ] **TC-VAL-019**: Compare valuations
  - Select multiple saved valuations
  - Click compare button
  - Verify comparison view displayed
  - Verify side-by-side comparison works
  - Verify differences highlighted

### 5.7 Subscription Limits & Access
- [ ] **TC-VAL-020**: Check subscription limits
  - Navigate to valuation terminal
  - Verify subscription tier displayed
  - Verify remaining valuations shown
  - Attempt valuation when limit reached
  - Verify upgrade prompt displayed
  - Verify limit enforcement works

- [ ] **TC-VAL-021**: Test valuation limits
  - Use up available valuations
  - Attempt additional valuation
  - Verify limit message displayed
  - Verify upgrade options shown

---

## 6. FMV Report Generation & Management

### 6.1 Report Request/Submission
- [ ] **TC-FMV-001**: Submit Spot Check report request
  - Navigate to report generation page
  - Select "Spot Check" tier ($250)
  - Fill in crane information
  - Submit request
  - Verify request created
  - Verify redirect to payment page
  - Verify report status: "Payment Pending"

- [ ] **TC-FMV-002**: Submit Professional report request
  - Navigate to report generation page
  - Select "Professional" tier ($995)
  - Fill in detailed crane information
  - Upload service records (if applicable)
  - Submit request
  - Verify request created
  - Verify redirect to payment page
  - Verify report status: "Payment Pending"

- [ ] **TC-FMV-003**: Submit Fleet Valuation request
  - Navigate to report generation page
  - Select "Fleet Valuation" tier (from $1,495)
  - Upload CSV file with multiple cranes OR
  - Add multiple cranes manually
  - Submit request
  - Verify request created
  - Verify fleet price calculated correctly
  - Verify redirect to payment page
  - Verify report status: "Payment Pending"

- [ ] **TC-FMV-004**: Report submission validation
  - Attempt submission with missing required fields
  - Verify validation errors
  - Attempt submission with invalid file format
  - Verify file validation error
  - Verify form not submitted

- [ ] **TC-FMV-005**: Upload service records
  - Navigate to report submission
  - Upload service records file
  - Verify file uploads successfully
  - Verify file displayed in form
  - Verify file accessible

- [ ] **TC-FMV-006**: Bulk file upload (Fleet)
  - Navigate to fleet valuation
  - Upload CSV file with crane data
  - Verify file parsed correctly
  - Verify crane data imported
  - Verify can edit imported data

### 6.2 Report Status Workflow
- [ ] **TC-FMV-007**: Report status: Payment Pending → Paid
  - Submit report request
  - Complete payment
  - Verify status changes to "Paid"
  - Verify status changes to "Submitted"
  - Verify email notification sent

- [ ] **TC-FMV-008**: Report status: Submitted → In Review
  - Admin marks report as "In Review"
  - Verify status updated in user's view
  - Verify email notification sent
  - Verify timeline updated

- [ ] **TC-FMV-009**: Report status: In Review → In Progress
  - Admin marks report as "In Progress"
  - Verify status updated
  - Verify email notification sent

- [ ] **TC-FMV-010**: Report status: In Progress → Need More Info
  - Admin requests more information
  - Verify status changes to "Need More Info"
  - Verify user receives notification
  - Verify user can provide additional info

- [ ] **TC-FMV-011**: Report status: In Progress → Delivered
  - Admin uploads PDF and marks as "Delivered"
  - Verify status changes to "Delivered"
  - Verify user receives email with PDF
  - Verify user can download PDF
  - Verify report appears in "My Reports"

- [ ] **TC-FMV-012**: Report status: Rejected
  - Admin rejects report
  - Verify status changes to "Rejected"
  - Verify user receives notification
  - Verify reason for rejection provided

- [ ] **TC-FMV-013**: Report status: Cancelled
  - User cancels report
  - Verify status changes to "Cancelled"
  - Verify refund processed (if applicable)
  - Verify email notification sent

### 6.3 Report Payment
- [ ] **TC-FMV-014**: Calculate report price
  - Select report type
  - Enter crane details
  - Verify price calculated correctly
  - For fleet: Verify price based on number of cranes

- [ ] **TC-FMV-015**: Create payment intent
  - Submit report request
  - Verify payment intent created
  - Verify Stripe payment form displayed
  - Verify amount correct

- [ ] **TC-FMV-016**: Process payment
  - Enter payment details (test card)
  - Submit payment
  - Verify payment processed
  - Verify payment confirmation
  - Verify report status updated
  - Verify receipt generated

- [ ] **TC-FMV-017**: Payment failure handling
  - Attempt payment with declined card
  - Verify error message displayed
  - Verify payment not processed
  - Verify report status remains "Payment Pending"
  - Verify can retry payment

### 6.4 Report Management
- [ ] **TC-FMV-018**: View report timeline
  - Navigate to report details
  - Click "Timeline" or view history
  - Verify all status changes displayed
  - Verify timestamps accurate
  - Verify admin actions visible

- [ ] **TC-FMV-019**: Update draft report
  - Create draft report
  - Make changes to report
  - Save as draft
  - Verify changes saved
  - Verify can continue editing later

- [ ] **TC-FMV-020**: Submit draft report
  - Open draft report
  - Complete all required fields
  - Submit report
  - Verify draft converted to submitted
  - Verify payment required

- [ ] **TC-FMV-021**: Delete report
  - Navigate to report
  - Click delete button
  - Confirm deletion
  - Verify report deleted
  - Verify email notification sent

### 6.5 Fallback Request
- [ ] **TC-FMV-022**: Submit fallback request
  - Navigate to fallback request form
  - Fill in request details (equipment info, reason, contact info)
  - Submit request
  - Verify request created
  - Verify request appears in admin panel
  - Verify admin notified
  - Verify confirmation email sent
  - Verify request status tracked

- [ ] **TC-FMV-023**: Fallback request validation
  - Attempt submission with missing required fields
  - Verify validation errors
  - Attempt submission with invalid data
  - Verify validation works correctly

### 6.6 Service Records Management
- [ ] **TC-FMV-024**: Upload service records
  - Navigate to report submission
  - Click "Upload Service Records"
  - Select valid file (PDF, images, documents)
  - Upload file
  - Verify file uploads successfully
  - Verify file displayed in form
  - Verify file accessible
  - Verify file size validation
  - Verify file type validation

- [ ] **TC-FMV-025**: View uploaded service records
  - Navigate to report with service records
  - Click "View Service Records"
  - Verify records displayed
  - Verify can download records
  - Verify records accessible

- [ ] **TC-FMV-026**: Delete service records
  - Navigate to uploaded service records
  - Click delete button
  - Confirm deletion
  - Verify records removed
  - Verify can re-upload

### 6.7 Bulk File Upload (Fleet Reports)
- [ ] **TC-FMV-027**: Upload CSV file for fleet
  - Navigate to fleet valuation
  - Click "Upload CSV" or "Bulk Upload"
  - Select valid CSV file
  - Upload file
  - Verify file parsed correctly
  - Verify crane data imported
  - Verify data validation performed
  - Verify can edit imported data
  - Verify can add additional cranes

- [ ] **TC-FMV-028**: CSV file validation
  - Attempt upload with invalid CSV format
  - Verify error message displayed
  - Attempt upload with missing required columns
  - Verify validation errors shown
  - Attempt upload with invalid data in CSV
  - Verify row-level errors displayed
  - Attempt upload with empty CSV
  - Verify error message

- [ ] **TC-FMV-029**: Edit imported fleet data
  - After CSV import
  - Edit individual crane data
  - Verify changes saved
  - Add new crane manually
  - Verify new crane added
  - Remove crane from fleet
  - Verify crane removed
  - Verify fleet price recalculated

### 6.8 Report Receipt & Invoicing
- [ ] **TC-FMV-030**: View report receipt
  - Navigate to paid report
  - Click "View Receipt" or "Invoice"
  - Verify receipt displayed
  - Verify receipt information accurate:
    - Report ID
    - Payment amount
    - Payment date
    - Payment method
    - User information
    - Report type
  - Verify can download receipt
  - Verify receipt format correct

- [ ] **TC-FMV-031**: Download receipt PDF
  - Navigate to receipt
  - Click "Download PDF"
  - Verify PDF downloads
  - Verify PDF content correct
  - Verify PDF format professional

### 6.9 Report Comments & Communication
- [ ] **TC-FMV-032**: Add comment to report
  - Navigate to report details
  - Add comment/note
  - Submit comment
  - Verify comment saved
  - Verify comment appears in timeline
  - Verify admin can see comment

- [ ] **TC-FMV-033**: View report communication history
  - Navigate to report
  - View communication/comment history
  - Verify all messages displayed
  - Verify timestamps accurate
  - Verify sender information shown

---

## 7. Payment Processing

### 7.1 Payment Integration
- [ ] **TC-PAY-001**: Stripe payment form loads
  - Navigate to payment page
  - Verify Stripe form displayed
  - Verify form fields present
  - Verify amount displayed correctly

- [ ] **TC-PAY-002**: Process successful payment
  - Enter valid test card (4242 4242 4242 4242)
  - Enter expiry date, CVC
  - Submit payment
  - Verify payment success
  - Verify redirect to confirmation page
  - Verify receipt generated
  - Verify email receipt sent

- [ ] **TC-PAY-003**: Payment with declined card
  - Enter declined test card (4000 0000 0000 0002)
  - Submit payment
  - Verify error message displayed
  - Verify payment not processed

- [ ] **TC-PAY-004**: Payment with insufficient funds
  - Enter card with insufficient funds (4000 0000 0000 9995)
  - Submit payment
  - Verify error message displayed

- [ ] **TC-PAY-005**: Payment webhook handling
  - Process payment
  - Verify webhook received
  - Verify webhook processed correctly
  - Verify payment status updated in database

### 7.2 Payment History
- [ ] **TC-PAY-006**: View payment history
  - Navigate to payment history/invoices
  - Verify all payments displayed
  - Verify payment details visible
  - Verify can download receipts

- [ ] **TC-PAY-007**: View payment receipt
  - Navigate to payment
  - Click "View Receipt"
  - Verify receipt displayed
  - Verify receipt information accurate
  - Verify can download receipt

### 7.3 Refunds
- [ ] **TC-PAY-008**: Request refund
  - Navigate to eligible payment
  - Request refund
  - Verify refund processed
  - Verify refund confirmation
  - Verify email notification sent

---

## 8. Admin Panel - Complete Coverage

### 8.1 Admin Authentication
- [ ] **TC-ADMIN-001**: Admin login
  - Navigate to admin login page
  - Enter admin credentials
  - Submit login
  - Verify successful login
  - Verify redirect to admin dashboard
  - Verify admin session created

- [ ] **TC-ADMIN-002**: Admin login with invalid credentials
  - Attempt login with wrong password
  - Verify error message
  - Verify no session created

- [ ] **TC-ADMIN-003**: Admin login with non-admin account
  - Attempt login with regular user credentials
  - Verify access denied
  - Verify redirect to regular login

- [ ] **TC-ADMIN-004**: Admin password reset
  - Navigate to admin password reset
  - Enter admin email
  - Submit request
  - Verify reset email sent
  - Complete password reset
  - Verify password updated

### 8.2 Admin Dashboard
- [ ] **TC-ADMIN-005**: View admin dashboard
  - Login as admin
  - Verify dashboard loads
  - Verify statistics displayed:
    - Total Users
    - Total Reports
    - Revenue
    - System Uptime
  - Verify statistics accurate

- [ ] **TC-ADMIN-006**: Dashboard activity feed
  - Verify recent activity displayed
  - Verify activity items accurate
  - Verify can filter activity

- [ ] **TC-ADMIN-007**: System status
  - Verify system health indicators
  - Verify API status
  - Verify database status
  - Verify service statuses

### 8.3 User Management
- [ ] **TC-ADMIN-008**: View all users
  - Navigate to Users page
  - Verify all users listed
  - Verify user details displayed
  - Verify pagination works

- [ ] **TC-ADMIN-009**: Search users
  - Enter search term
  - Verify search results
  - Verify search works correctly

- [ ] **TC-ADMIN-010**: Filter users
  - Apply filters (role, status, subscription)
  - Verify filtered results
  - Verify filters work correctly

- [ ] **TC-ADMIN-011**: View user details
  - Click on user
  - Verify user details page loads
  - Verify all user information displayed
  - Verify user's reports visible
  - Verify user's payments visible

- [ ] **TC-ADMIN-012**: Create new user
  - Click "Create User" or similar
  - Fill user form
  - Submit form
  - Verify user created
  - Verify email notification sent

- [ ] **TC-ADMIN-013**: Update user
  - Navigate to user details
  - Update user information
  - Save changes
  - Verify changes saved
  - Verify email notification sent

- [ ] **TC-ADMIN-014**: Deactivate user
  - Navigate to user
  - Click "Deactivate"
  - Confirm action
  - Verify user deactivated
  - Verify user cannot login

- [ ] **TC-ADMIN-015**: Activate user
  - Navigate to deactivated user
  - Click "Activate"
  - Verify user activated
  - Verify user can login

- [ ] **TC-ADMIN-016**: Delete user
  - Navigate to user
  - Click "Delete"
  - Confirm deletion
  - Verify user deleted
  - Verify user data removed (GDPR compliance)

- [ ] **TC-ADMIN-017**: Change user role
  - Navigate to user
  - Change user role
  - Save changes
  - Verify role updated
  - Verify permissions updated

- [ ] **TC-ADMIN-018**: Bulk user operations
  - Select multiple users
  - Perform bulk action (activate, deactivate, delete)
  - Verify action applied to all selected
  - Verify confirmation message

- [ ] **TC-ADMIN-019**: Export users
  - Click "Export Users"
  - Verify export file generated
  - Verify file contains all user data
  - Verify file format correct (CSV/Excel)

### 8.4 FMV Reports Management
- [ ] **TC-ADMIN-020**: View all FMV reports
  - Navigate to FMV Reports page
  - Verify all reports listed
  - Verify report details displayed
  - Verify pagination works

- [ ] **TC-ADMIN-021**: Filter reports
  - Apply status filter
  - Apply date range filter
  - Apply user filter
  - Verify filters work correctly

- [ ] **TC-ADMIN-022**: Search reports
  - Enter search term
  - Verify search results
  - Verify search works

- [ ] **TC-ADMIN-023**: View report details
  - Click on report
  - Verify report details page loads
  - Verify all report information displayed
  - Verify customer information visible
  - Verify payment information visible
  - Verify timeline visible

- [ ] **TC-ADMIN-024**: Update report status
  - Navigate to report
  - Change status (e.g., In Review → In Progress)
  - Save changes
  - Verify status updated
  - Verify user notified
  - Verify timeline updated

- [ ] **TC-ADMIN-025**: Upload report PDF
  - Navigate to report
  - Click "Upload PDF"
  - Select PDF file
  - Upload file
  - Verify PDF uploaded
  - Verify PDF accessible
  - Verify status updated to "Delivered"
  - Verify user notified

- [ ] **TC-ADMIN-026**: Send report email
  - After uploading PDF
  - Click "Send Email" or auto-send
  - Verify email sent to user
  - Verify email contains PDF link
  - Verify email log recorded

- [ ] **TC-ADMIN-027**: Request more information
  - Navigate to report
  - Click "Request More Info"
  - Enter message
  - Send request
  - Verify status updated
  - Verify user notified
  - Verify user can respond

- [ ] **TC-ADMIN-028**: Reject report
  - Navigate to report
  - Click "Reject"
  - Enter rejection reason
  - Confirm rejection
  - Verify status updated
  - Verify user notified
  - Verify refund processed (if applicable)

- [ ] **TC-ADMIN-029**: Delete report
  - Navigate to report
  - Click "Delete"
  - Confirm deletion
  - Verify report deleted
  - Verify user notified

- [ ] **TC-ADMIN-030**: View report statistics
  - Navigate to reports statistics
  - Verify statistics displayed:
    - Total reports
    - Reports by status
    - Revenue by report type
    - Average turnaround time
  - Verify statistics accurate

- [ ] **TC-ADMIN-031**: Check draft reminders
  - Navigate to draft reminders
  - Run draft reminder check
  - Verify reminders sent for overdue drafts
  - Verify reminder emails sent

- [ ] **TC-ADMIN-032**: Check overdue reports
  - Navigate to overdue reports check
  - Run overdue check
  - Verify overdue reports identified
  - Verify alerts sent

### 8.5 Payments Management
- [ ] **TC-ADMIN-033**: View all payments
  - Navigate to Payments page
  - Verify all payments listed
  - Verify payment details displayed
  - Verify filters work

- [ ] **TC-ADMIN-034**: View payment details
  - Click on payment
  - Verify payment details displayed
  - Verify user information visible
  - Verify report information visible
  - Verify receipt available

- [ ] **TC-ADMIN-035**: Process refund
  - Navigate to payment
  - Click "Refund"
  - Enter refund amount
  - Process refund
  - Verify refund processed
  - Verify Stripe refund initiated
  - Verify user notified

- [ ] **TC-ADMIN-036**: View payment statistics
  - Navigate to payment statistics
  - Verify statistics displayed:
    - Total revenue
    - Revenue by period
    - Payment methods
    - Refund statistics
  - Verify statistics accurate

- [ ] **TC-ADMIN-037**: Payment reconciliation
  - Navigate to payment reconciliation
  - Run reconciliation
  - Verify payments reconciled
  - Verify discrepancies identified
  - Verify reconciliation report generated

### 8.6 Cranes/Equipment Management
- [ ] **TC-ADMIN-038**: View all cranes
  - Navigate to Cranes page
  - Verify all cranes listed
  - Verify crane details displayed
  - Verify filters work

- [ ] **TC-ADMIN-039**: Add new crane
  - Click "Add Crane"
  - Fill crane form
  - Submit form
  - Verify crane added
  - Verify crane appears in list

- [ ] **TC-ADMIN-040**: Update crane
  - Navigate to crane
  - Update crane information
  - Save changes
  - Verify changes saved

- [ ] **TC-ADMIN-041**: Delete crane
  - Navigate to crane
  - Click "Delete"
  - Confirm deletion
  - Verify crane deleted

### 8.7 Valuations Management
- [ ] **TC-ADMIN-042**: View all valuations
  - Navigate to Valuations page
  - Verify all valuations listed
  - Verify valuation details displayed
  - Verify filters work

- [ ] **TC-ADMIN-043**: View valuation details
  - Click on valuation
  - Verify valuation details displayed
  - Verify calculation details visible
  - Verify comparable sales visible

### 8.8 Consultations Management
- [ ] **TC-ADMIN-044**: View all consultations
  - Navigate to Consultations page
  - Verify all consultations listed
  - Verify consultation details displayed

- [ ] **TC-ADMIN-045**: View consultation details
  - Click on consultation
  - Verify consultation details displayed
  - Verify contact information visible
  - Verify message visible

- [ ] **TC-ADMIN-046**: Update consultation status
  - Navigate to consultation
  - Update status (New, Contacted, Completed, etc.)
  - Save changes
  - Verify status updated

### 8.9 Analytics & Reporting
- [ ] **TC-ADMIN-047**: View analytics dashboard
  - Navigate to Analytics page
  - Verify analytics displayed
  - Verify charts/graphs load
  - Verify data accurate

- [ ] **TC-ADMIN-048**: View user analytics
  - Navigate to user analytics
  - Verify user statistics displayed
  - Verify user growth charts
  - Verify user activity metrics

- [ ] **TC-ADMIN-049**: View revenue analytics
  - Navigate to revenue analytics
  - Verify revenue statistics displayed
  - Verify revenue charts
  - Verify revenue trends visible

- [ ] **TC-ADMIN-050**: Export analytics data
  - Navigate to analytics
  - Click "Export"
  - Verify export file generated
  - Verify file contains analytics data

### 8.10 System Settings
- [ ] **TC-ADMIN-051**: View system settings
  - Navigate to Settings page
  - Verify all settings displayed
  - Verify settings organized by category

- [ ] **TC-ADMIN-052**: Update general settings
  - Navigate to general settings
  - Update settings
  - Save changes
  - Verify changes saved
  - Verify changes applied

- [ ] **TC-ADMIN-053**: Update email settings
  - Navigate to email settings
  - Update SMTP settings
  - Test email configuration
  - Save changes
  - Verify email works

- [ ] **TC-ADMIN-054**: Update payment settings
  - Navigate to payment settings
  - Update Stripe keys
  - Test payment connection
  - Save changes
  - Verify payments work

### 8.11 Algorithm Management
- [ ] **TC-ADMIN-055**: View algorithm settings
  - Navigate to Algorithm page
  - Verify algorithm parameters displayed
  - Verify current algorithm version

- [ ] **TC-ADMIN-056**: Update algorithm parameters
  - Navigate to algorithm settings
  - Update parameters
  - Save changes
  - Verify parameters updated
  - Verify valuations use new parameters

### 8.12 Security Management
- [ ] **TC-ADMIN-057**: View security settings
  - Navigate to Security page
  - Verify security settings displayed
  - Verify 2FA settings visible

- [ ] **TC-ADMIN-058**: Enable/disable 2FA
  - Navigate to 2FA settings
  - Enable 2FA
  - Verify 2FA enabled
  - Test 2FA login
  - Disable 2FA
  - Verify 2FA disabled

- [ ] **TC-ADMIN-059**: View audit logs
  - Navigate to Audit Logs
  - Verify audit logs displayed
  - Verify logs include all admin actions
  - Verify can filter/search logs

- [ ] **TC-ADMIN-060**: View active sessions
  - Navigate to Sessions page
  - Verify active sessions displayed
  - Verify session details visible
  - Verify can terminate sessions

### 8.13 Email Management
- [ ] **TC-ADMIN-061**: View email templates
  - Navigate to Email Management
  - Verify all email templates listed
  - Verify template details displayed

- [ ] **TC-ADMIN-062**: View email template
  - Click on email template
  - Verify template content displayed
  - Verify template variables visible

- [ ] **TC-ADMIN-063**: Edit email template
  - Navigate to template
  - Edit template content
  - Save changes
  - Verify template updated
  - Verify test email sent

- [ ] **TC-ADMIN-064**: Create email template
  - Click "Create Template"
  - Fill template form
  - Save template
  - Verify template created

- [ ] **TC-ADMIN-065**: Delete email template
  - Navigate to template
  - Delete template
  - Verify template deleted

- [ ] **TC-ADMIN-066**: View email logs
  - Navigate to email logs
  - Verify email logs displayed
  - Verify can filter/search logs
  - Verify email status visible

- [ ] **TC-ADMIN-067**: View email statistics
  - Navigate to email statistics
  - Verify statistics displayed:
    - Emails sent
    - Delivery rate
    - Open rate
    - Bounce rate
  - Verify statistics accurate

### 8.14 Data Management
- [ ] **TC-ADMIN-068**: View data sources
  - Navigate to Data Sources
  - Verify data sources listed
  - Verify source status visible

- [ ] **TC-ADMIN-069**: View database information
  - Navigate to Database page
  - Verify database statistics displayed
  - Verify table information visible

- [ ] **TC-ADMIN-070**: Export data
  - Navigate to data export
  - Select data to export
  - Export data
  - Verify export file generated
  - Verify file contains requested data

- [ ] **TC-ADMIN-071**: Import data
  - Navigate to data import
  - Upload import file
  - Verify file validated
  - Process import
  - Verify data imported

- [ ] **TC-ADMIN-072**: Backup data
  - Navigate to backup
  - Create backup
  - Verify backup created
  - Verify backup accessible

- [ ] **TC-ADMIN-073**: Restore data
  - Navigate to restore
  - Select backup
  - Restore data
  - Verify data restored

### 8.15 Bulk Operations
- [ ] **TC-ADMIN-074**: Bulk activate users
  - Select multiple users
  - Click "Bulk Activate"
  - Confirm action
  - Verify all selected users activated

- [ ] **TC-ADMIN-075**: Bulk deactivate users
  - Select multiple users
  - Click "Bulk Deactivate"
  - Confirm action
  - Verify all selected users deactivated

- [ ] **TC-ADMIN-076**: Bulk delete users
  - Select multiple users
  - Click "Bulk Delete"
  - Confirm action
  - Verify all selected users deleted

- [ ] **TC-ADMIN-077**: Bulk export
  - Select multiple items
  - Click "Export"
  - Verify export file contains all selected items

### 8.16 GDPR Compliance
- [ ] **TC-ADMIN-078**: View GDPR requests
  - Navigate to GDPR Compliance page
  - Verify data requests listed
  - Verify request status visible

- [ ] **TC-ADMIN-079**: Process data export request
  - Navigate to data request
  - Process export request
  - Verify data exported
  - Verify user notified

- [ ] **TC-ADMIN-080**: Process data deletion request
  - Navigate to deletion request
  - Process deletion request
  - Verify data deleted
  - Verify user notified

### 8.17 System Health
- [ ] **TC-ADMIN-081**: View system health
  - Navigate to System Health page
  - Verify health indicators displayed
  - Verify all services status visible
  - Verify performance metrics displayed

- [ ] **TC-ADMIN-082**: View API health
  - Verify API endpoints status
  - Verify response times
  - Verify error rates

- [ ] **TC-ADMIN-083**: View database health
  - Verify database connection status
  - Verify database performance
  - Verify database size

### 8.18 Admin Users Management
- [ ] **TC-ADMIN-084**: View admin users
  - Navigate to Admin Users page
  - Verify all admin users listed
  - Verify admin roles displayed

- [ ] **TC-ADMIN-085**: Create admin user
  - Click "Create Admin"
  - Fill admin form
  - Assign admin role
  - Save admin
  - Verify admin created

- [ ] **TC-ADMIN-086**: Update admin user
  - Navigate to admin user
  - Update admin information
  - Save changes
  - Verify changes saved

- [ ] **TC-ADMIN-087**: Delete admin user
  - Navigate to admin user
  - Delete admin
  - Verify admin deleted

### 8.19 Roles & Permissions
- [ ] **TC-ADMIN-088**: View roles
  - Navigate to Roles page
  - Verify all roles listed
  - Verify role permissions displayed

- [ ] **TC-ADMIN-089**: Create role
  - Click "Create Role"
  - Define role permissions
  - Save role
  - Verify role created

- [ ] **TC-ADMIN-090**: Update role
  - Navigate to role
  - Update permissions
  - Save changes
  - Verify role updated

- [ ] **TC-ADMIN-091**: Delete role
  - Navigate to role
  - Delete role
  - Verify role deleted

### 8.20 Content Management
- [ ] **TC-ADMIN-092**: View content
  - Navigate to Content page
  - Verify content items listed
  - Verify content types displayed
  - Verify search/filter works

- [ ] **TC-ADMIN-093**: Edit content
  - Navigate to content item
  - Edit content
  - Save changes
  - Verify content updated
  - Verify changes visible on website
  - Verify preview functionality works

- [ ] **TC-ADMIN-094**: Create content
  - Click "Create Content"
  - Fill content form
  - Save content
  - Verify content created
  - Verify appears in list

- [ ] **TC-ADMIN-095**: Delete content
  - Navigate to content item
  - Delete content
  - Confirm deletion
  - Verify content deleted
  - Verify removed from website

### 8.21 Fallback Requests Management
- [ ] **TC-ADMIN-096**: View fallback requests
  - Navigate to Fallback Requests page
  - Verify all requests listed
  - Verify request details displayed
  - Verify status visible
  - Verify filters work

- [ ] **TC-ADMIN-097**: View fallback request details
  - Click on fallback request
  - Verify request details displayed
  - Verify customer information visible
  - Verify equipment information visible
  - Verify request reason displayed

- [ ] **TC-ADMIN-098**: Update fallback request status
  - Navigate to fallback request
  - Update status (New, In Progress, Completed, Rejected)
  - Add admin notes
  - Save changes
  - Verify status updated
  - Verify user notified

- [ ] **TC-ADMIN-099**: Convert fallback to report
  - Navigate to fallback request
  - Click "Convert to Report"
  - Verify report created
  - Verify fallback request linked
  - Verify user notified

### 8.22 Admin Impersonation
- [ ] **TC-ADMIN-100**: Impersonate user
  - Navigate to user details
  - Click "Impersonate User"
  - Confirm impersonation
  - Verify logged in as user
  - Verify can access user's data
  - Verify impersonation indicator displayed

- [ ] **TC-ADMIN-101**: End impersonation
  - While impersonating user
  - Click "End Impersonation"
  - Verify returned to admin panel
  - Verify admin session restored
  - Verify impersonation logged

### 8.23 Draft Reminders Management
- [ ] **TC-ADMIN-102**: View draft reminders
  - Navigate to Draft Reminders page
  - Verify overdue drafts listed
  - Verify reminder status displayed
  - Verify filters work

- [ ] **TC-ADMIN-103**: Send draft reminders
  - Navigate to draft reminders
  - Select drafts to remind
  - Click "Send Reminders"
  - Verify reminders sent
  - Verify emails delivered
  - Verify reminder status updated

- [ ] **TC-ADMIN-104**: Check draft reminders automatically
  - Navigate to draft reminders check
  - Run automatic check
  - Verify overdue drafts identified
  - Verify reminders sent automatically
  - Verify check logged

### 8.24 Overdue Reports Management
- [ ] **TC-ADMIN-105**: View overdue reports
  - Navigate to Overdue Reports page
  - Verify overdue reports listed
  - Verify days overdue displayed
  - Verify filters work

- [ ] **TC-ADMIN-106**: Check overdue reports
  - Navigate to overdue reports check
  - Run overdue check
  - Verify overdue reports identified
  - Verify alerts sent
  - Verify check logged

- [ ] **TC-ADMIN-107**: Handle overdue report
  - Navigate to overdue report
  - Update report status
  - Add notes about delay
  - Notify user
  - Verify actions logged

### 8.25 Payment Reconciliation
- [ ] **TC-ADMIN-108**: View payment reconciliation
  - Navigate to Payment Reconciliation page
  - Verify reconciliation data displayed
  - Verify discrepancies highlighted
  - Verify filters work

- [ ] **TC-ADMIN-109**: Run payment reconciliation
  - Navigate to reconciliation
  - Click "Run Reconciliation"
  - Verify reconciliation processed
  - Verify discrepancies identified
  - Verify reconciliation report generated
  - Verify can download report

- [ ] **TC-ADMIN-110**: Resolve reconciliation discrepancies
  - Navigate to discrepancy
  - Review discrepancy details
  - Resolve discrepancy
  - Add resolution notes
  - Verify discrepancy marked resolved

### 8.26 Admin Profile
- [ ] **TC-ADMIN-111**: View admin profile
  - Navigate to Profile page
  - Verify profile information displayed
  - Verify admin role displayed
  - Verify permissions visible

- [ ] **TC-ADMIN-112**: Update admin profile
  - Update profile information (name, email, etc.)
  - Save changes
  - Verify changes saved
  - Verify changes reflected immediately
  - Verify email notification sent if email changed

- [ ] **TC-ADMIN-113**: Change admin password
  - Navigate to profile
  - Enter current password
  - Enter new password
  - Confirm new password
  - Save changes
  - Verify password updated
  - Verify can login with new password
  - Verify email notification sent

### 8.27 Core Logic & Algorithm Management
- [ ] **TC-ADMIN-114**: View core logic settings
  - Navigate to Core Logic page
  - Verify algorithm parameters displayed
  - Verify current algorithm version
  - Verify algorithm status

- [ ] **TC-ADMIN-115**: Update algorithm parameters
  - Navigate to algorithm settings
  - Update valuation parameters
  - Update scoring weights
  - Save changes
  - Verify parameters updated
  - Verify valuations use new parameters
  - Verify changes logged

- [ ] **TC-ADMIN-116**: Test algorithm changes
  - After updating parameters
  - Run test valuation
  - Verify results reflect changes
  - Verify algorithm works correctly
  - Revert if issues found

### 8.28 Data Sources Management
- [ ] **TC-ADMIN-117**: View data sources
  - Navigate to Data Sources page
  - Verify all data sources listed
  - Verify source status displayed
  - Verify last update time shown
  - Verify connection status visible

- [ ] **TC-ADMIN-118**: Refresh data source
  - Navigate to data source
  - Click "Refresh" or "Sync"
  - Verify refresh initiated
  - Verify status updates
  - Verify data updated
  - Verify refresh logged

- [ ] **TC-ADMIN-119**: Configure data source
  - Navigate to data source
  - Update configuration
  - Test connection
  - Save changes
  - Verify configuration saved
  - Verify connection works

### 8.29 Real-time Data & Live Feeds
- [ ] **TC-ADMIN-120**: View real-time data feeds
  - Navigate to Real-time Feeds page
  - Verify active feeds displayed
  - Verify feed status shown
  - Verify data update frequency visible

- [ ] **TC-ADMIN-121**: Manage data refresh
  - Navigate to data refresh settings
  - Configure refresh intervals
  - Save settings
  - Verify refresh schedule updated
  - Verify automatic refresh works

### 8.30 Enhanced Analytics
- [ ] **TC-ADMIN-122**: View comprehensive analytics
  - Navigate to Analytics page
  - Verify all analytics sections displayed
  - Verify charts load correctly
  - Verify data accurate
  - Verify date range filters work

- [ ] **TC-ADMIN-123**: Export analytics reports
  - Navigate to analytics
  - Select date range
  - Click "Export Report"
  - Select format (PDF, Excel, CSV)
  - Verify report generated
  - Verify report contains all data

---

## 9. Equipment Management

### 9.1 Equipment CRUD Operations
- [ ] **TC-EQUIP-001**: Create equipment record
  - Navigate to Add Equipment page
  - Fill equipment form (manufacturer, model, serial number, etc.)
  - Submit form
  - Verify equipment created
  - Verify equipment appears in list
  - Verify success message displayed

- [ ] **TC-EQUIP-002**: View equipment list
  - Navigate to Equipment page
  - Verify all equipment listed
  - Verify equipment details displayed
  - Verify pagination works
  - Verify search functionality works
  - Verify filters work

- [ ] **TC-EQUIP-003**: View equipment details
  - Click on equipment item
  - Verify equipment details page loads
  - Verify all information displayed
  - Verify maintenance records visible
  - Verify inspection records visible
  - Verify valuation history visible

- [ ] **TC-EQUIP-004**: Update equipment
  - Navigate to equipment details
  - Update equipment information
  - Save changes
  - Verify changes saved
  - Verify changes reflected immediately

- [ ] **TC-EQUIP-005**: Delete equipment
  - Navigate to equipment
  - Click delete button
  - Confirm deletion
  - Verify equipment deleted
  - Verify removed from list

### 9.2 Equipment Maintenance Records
- [ ] **TC-EQUIP-006**: Add maintenance record
  - Navigate to equipment
  - Click "Add Maintenance Record"
  - Fill maintenance form (date, type, description, cost)
  - Submit form
  - Verify record created
  - Verify appears in maintenance history

- [ ] **TC-EQUIP-007**: View maintenance history
  - Navigate to equipment
  - View maintenance records
  - Verify all records displayed
  - Verify records sorted by date
  - Verify can filter records

- [ ] **TC-EQUIP-008**: Update maintenance record
  - Navigate to maintenance record
  - Update record information
  - Save changes
  - Verify changes saved

- [ ] **TC-EQUIP-009**: View upcoming maintenance
  - Navigate to upcoming maintenance
  - Verify upcoming maintenance listed
  - Verify due dates displayed
  - Verify can filter by date range

- [ ] **TC-EQUIP-010**: View overdue maintenance
  - Navigate to overdue maintenance
  - Verify overdue items listed
  - Verify overdue days displayed
  - Verify alerts shown

### 9.3 Equipment Inspections
- [ ] **TC-EQUIP-011**: Add inspection record
  - Navigate to equipment
  - Click "Add Inspection"
  - Fill inspection form
  - Upload inspection documents
  - Submit form
  - Verify inspection recorded
  - Verify documents attached

- [ ] **TC-EQUIP-012**: View inspection history
  - Navigate to equipment
  - View inspection records
  - Verify all inspections displayed
  - Verify inspection documents accessible
  - Verify can download documents

- [ ] **TC-EQUIP-013**: Update inspection record
  - Navigate to inspection
  - Update inspection details
  - Save changes
  - Verify changes saved

### 9.4 Equipment Valuations
- [ ] **TC-EQUIP-014**: Add valuation record
  - Navigate to equipment
  - Click "Add Valuation"
  - Fill valuation form
  - Link to FMV report (if applicable)
  - Submit form
  - Verify valuation recorded
  - Verify appears in valuation history

- [ ] **TC-EQUIP-015**: View valuation history
  - Navigate to equipment
  - View valuation records
  - Verify all valuations displayed
  - Verify valuation trends visible
  - Verify can export history

### 9.5 Equipment Companies
- [ ] **TC-EQUIP-016**: Create company
  - Navigate to Companies page
  - Click "Create Company"
  - Fill company form
  - Submit form
  - Verify company created
  - Verify appears in list

- [ ] **TC-EQUIP-017**: View company equipment
  - Navigate to company
  - View company equipment list
  - Verify all equipment displayed
  - Verify equipment details visible
  - Verify can filter equipment

- [ ] **TC-EQUIP-018**: Link equipment to company
  - Navigate to equipment
  - Assign to company
  - Save changes
  - Verify equipment linked
  - Verify appears in company list

### 9.6 Equipment Statistics
- [ ] **TC-EQUIP-019**: View equipment statistics
  - Navigate to equipment statistics
  - Verify statistics displayed:
    - Total equipment
    - Equipment by type
    - Maintenance status
    - Valuation trends
  - Verify statistics accurate
  - Verify charts/graphs displayed

- [ ] **TC-EQUIP-020**: Export equipment data
  - Navigate to equipment list
  - Click "Export"
  - Select format (CSV, Excel)
  - Verify export file generated
  - Verify file contains all data

### 9.7 Live Equipment Data
- [ ] **TC-EQUIP-021**: View live equipment data
  - Navigate to live equipment feed
  - Verify real-time data displayed
  - Verify data updates automatically
  - Verify data accurate
  - Verify no flickering

---

## 10. API Endpoint Testing

### 10.1 Authentication API
- [ ] **TC-API-001**: POST /api/v1/auth/register
  - Send registration request
  - Verify user created
  - Verify response contains token
  - Verify email sent

- [ ] **TC-API-002**: POST /api/v1/auth/login
  - Send login request
  - Verify authentication successful
  - Verify JWT token returned
  - Verify token valid

- [ ] **TC-API-003**: POST /api/v1/auth/verify-email
  - Send verification request
  - Verify email verified
  - Verify response correct

- [ ] **TC-API-004**: POST /api/v1/auth/resend-verification
  - Send resend request
  - Verify email sent
  - Verify response correct

- [ ] **TC-API-005**: POST /api/v1/auth/forgot-password
  - Send forgot password request
  - Verify reset email sent
  - Verify response correct

- [ ] **TC-API-006**: POST /api/v1/auth/reset-password
  - Send reset password request
  - Verify password reset
  - Verify response correct

- [ ] **TC-API-007**: GET /api/v1/auth/profile
  - Send profile request with valid token
  - Verify profile data returned
  - Verify response correct

- [ ] **TC-API-008**: API authentication with invalid token
  - Send request with invalid token
  - Verify 401 Unauthorized
  - Verify error message

- [ ] **TC-API-009**: API authentication with expired token
  - Send request with expired token
  - Verify 401 Unauthorized
  - Verify error message

### 10.2 FMV Reports API
- [ ] **TC-API-010**: POST /api/v1/fmv-reports/submit
  - Send report submission
  - Verify report created
  - Verify response correct
  - Verify report status correct

- [ ] **TC-API-011**: GET /api/v1/fmv-reports/user/{user_id}
  - Send request for user reports
  - Verify reports returned
  - Verify response correct

- [ ] **TC-API-012**: GET /api/v1/fmv-reports/{report_id}
  - Send request for report details
  - Verify report data returned
  - Verify response correct

- [ ] **TC-API-013**: PUT /api/v1/fmv-reports/{report_id}/status
  - Send status update request
  - Verify status updated
  - Verify response correct

- [ ] **TC-API-014**: POST /api/v1/fmv-reports/{report_id}/upload-pdf
  - Send PDF upload request
  - Verify PDF uploaded
  - Verify response correct

- [ ] **TC-API-015**: POST /api/v1/fmv-reports/{report_id}/payment
  - Send payment request
  - Verify payment processed
  - Verify response correct

- [ ] **TC-API-016**: GET /api/v1/fmv-reports/calculate-fleet-price
  - Send fleet price calculation
  - Verify price calculated
  - Verify response correct

- [ ] **TC-API-017**: GET /api/v1/fmv-reports/{report_id}/timeline
  - Send timeline request
  - Verify timeline returned
  - Verify response correct

### 10.3 Valuation API
- [ ] **TC-API-018**: POST /api/v1/valuation/value-crane
  - Send valuation request
  - Verify valuation calculated
  - Verify response contains FMV
  - Verify response contains scores

- [ ] **TC-API-019**: POST /api/v1/valuation/value-crane-enhanced
  - Send enhanced valuation request
  - Verify enhanced valuation calculated
  - Verify response correct

- [ ] **TC-API-020**: POST /api/v1/valuation/market-analysis
  - Send market analysis request
  - Verify analysis returned
  - Verify response correct

- [ ] **TC-API-021**: POST /api/v1/valuation/fleet-optimization
  - Send fleet optimization request
  - Verify optimization calculated
  - Verify response correct

- [ ] **TC-API-022**: GET /api/v1/valuation/manufacturers
  - Send manufacturers request
  - Verify manufacturers returned
  - Verify response correct

- [ ] **TC-API-023**: GET /api/v1/valuation/regions
  - Send regions request
  - Verify regions returned
  - Verify response correct

### 10.4 Equipment API
- [ ] **TC-API-024**: POST /api/v1/equipment/
  - Send equipment creation request
  - Verify equipment created
  - Verify response correct

- [ ] **TC-API-025**: GET /api/v1/equipment/{equipment_id}
  - Send equipment request
  - Verify equipment data returned
  - Verify response correct

- [ ] **TC-API-026**: PUT /api/v1/equipment/{equipment_id}
  - Send equipment update request
  - Verify equipment updated
  - Verify response correct

- [ ] **TC-API-027**: DELETE /api/v1/equipment/{equipment_id}
  - Send equipment deletion request
  - Verify equipment deleted
  - Verify response correct

- [ ] **TC-API-028**: GET /api/v1/equipment/
  - Send equipment list request
  - Verify equipment list returned
  - Verify pagination works

### 10.5 Admin API
- [ ] **TC-API-029**: POST /api/v1/admin/auth/login
  - Send admin login request
  - Verify admin authenticated
  - Verify admin token returned

- [ ] **TC-API-030**: GET /api/v1/admin/dashboard/stats
  - Send dashboard stats request
  - Verify stats returned
  - Verify response correct

- [ ] **TC-API-031**: GET /api/v1/admin/users
  - Send users list request
  - Verify users returned
  - Verify pagination works

- [ ] **TC-API-032**: GET /api/v1/admin/fmv-reports
  - Send admin reports request
  - Verify reports returned
  - Verify filters work

- [ ] **TC-API-033**: PUT /api/v1/admin/fmv-reports/{report_id}
  - Send report update request
  - Verify report updated
  - Verify response correct

### 10.6 Notifications API
- [ ] **TC-API-034**: GET /api/v1/notifications
  - Send notifications request
  - Verify notifications returned
  - Verify response correct

- [ ] **TC-API-035**: POST /api/v1/notifications/{notification_id}/read
  - Send mark as read request
  - Verify notification marked as read
  - Verify response correct

- [ ] **TC-API-036**: POST /api/v1/notifications/read-all
  - Send mark all as read request
  - Verify all notifications marked as read
  - Verify response correct

### 10.7 Consultation API
- [ ] **TC-API-037**: POST /api/v1/consultation/submit
  - Send consultation submission
  - Verify consultation created
  - Verify response correct

- [ ] **TC-API-038**: GET /api/v1/consultation
  - Send consultations list request
  - Verify consultations returned
  - Verify response correct

### 10.8 Newsletter API
- [ ] **TC-API-039**: POST /api/v1/newsletter/subscribe
  - Send subscription request
  - Verify subscription created
  - Verify response correct

- [ ] **TC-API-040**: POST /api/v1/newsletter/unsubscribe
  - Send unsubscription request
  - Verify unsubscription processed
  - Verify response correct

### 10.9 Health Check API
- [ ] **TC-API-041**: GET /api/v1/health
  - Send health check request
  - Verify health status returned
  - Verify response indicates healthy

- [ ] **TC-API-042**: GET /api/v1/database/health
  - Send database health check
  - Verify database status returned
  - Verify response indicates healthy

### 10.10 Equipment API Endpoints
- [ ] **TC-API-047**: POST /api/v1/equipment/
  - Send equipment creation request
  - Verify equipment created
  - Verify response correct
  - Verify equipment data returned

- [ ] **TC-API-048**: GET /api/v1/equipment/{equipment_id}
  - Send equipment request
  - Verify equipment data returned
  - Verify response correct
  - Verify all fields present

- [ ] **TC-API-049**: PUT /api/v1/equipment/{equipment_id}
  - Send equipment update request
  - Verify equipment updated
  - Verify response correct
  - Verify updated data returned

- [ ] **TC-API-050**: DELETE /api/v1/equipment/{equipment_id}
  - Send equipment deletion request
  - Verify equipment deleted
  - Verify response correct
  - Verify equipment no longer accessible

- [ ] **TC-API-051**: GET /api/v1/equipment/
  - Send equipment list request
  - Verify equipment list returned
  - Verify pagination works
  - Verify filters work

- [ ] **TC-API-052**: POST /api/v1/equipment/{equipment_id}/maintenance
  - Send maintenance record creation
  - Verify maintenance recorded
  - Verify response correct

- [ ] **TC-API-053**: GET /api/v1/equipment/{equipment_id}/maintenance
  - Send maintenance history request
  - Verify maintenance records returned
  - Verify response correct

- [ ] **TC-API-054**: POST /api/v1/equipment/{equipment_id}/inspections
  - Send inspection record creation
  - Verify inspection recorded
  - Verify response correct

- [ ] **TC-API-055**: GET /api/v1/equipment/{equipment_id}/inspections
  - Send inspection history request
  - Verify inspection records returned
  - Verify response correct

- [ ] **TC-API-056**: POST /api/v1/equipment/{equipment_id}/valuations
  - Send valuation record creation
  - Verify valuation recorded
  - Verify response correct

- [ ] **TC-API-057**: GET /api/v1/equipment/{equipment_id}/valuations
  - Send valuation history request
  - Verify valuation records returned
  - Verify response correct

- [ ] **TC-API-058**: GET /api/v1/equipment/stats/overview
  - Send equipment statistics request
  - Verify statistics returned
  - Verify response correct

- [ ] **TC-API-059**: GET /api/v1/equipment/live
  - Send live equipment data request
  - Verify live data returned
  - Verify data updates

### 10.11 Admin Email Management API
- [ ] **TC-API-060**: GET /api/v1/admin/email/templates
  - Send templates list request
  - Verify templates returned
  - Verify response correct

- [ ] **TC-API-061**: POST /api/v1/admin/email/templates
  - Send template creation request
  - Verify template created
  - Verify response correct

- [ ] **TC-API-062**: PUT /api/v1/admin/email/templates/{template_id}
  - Send template update request
  - Verify template updated
  - Verify response correct

- [ ] **TC-API-063**: DELETE /api/v1/admin/email/templates/{template_id}
  - Send template deletion request
  - Verify template deleted
  - Verify response correct

- [ ] **TC-API-064**: GET /api/v1/admin/email/logs
  - Send email logs request
  - Verify logs returned
  - Verify pagination works

- [ ] **TC-API-065**: GET /api/v1/admin/email/stats/summary
  - Send email statistics request
  - Verify statistics returned
  - Verify response correct

### 10.12 Admin Bulk Operations API
- [ ] **TC-API-066**: POST /api/v1/admin/bulk/users/activate
  - Send bulk activate request
  - Verify users activated
  - Verify response correct

- [ ] **TC-API-067**: POST /api/v1/admin/bulk/users/deactivate
  - Send bulk deactivate request
  - Verify users deactivated
  - Verify response correct

- [ ] **TC-API-068**: POST /api/v1/admin/bulk/users/export
  - Send bulk export request
  - Verify export file generated
  - Verify file downloadable

- [ ] **TC-API-069**: POST /api/v1/admin/bulk/users/import
  - Send bulk import request
  - Upload import file
  - Verify users imported
  - Verify response correct

### 10.13 Admin GDPR API
- [ ] **TC-API-070**: POST /api/v1/admin/gdpr/export/{user_id}
  - Send GDPR export request
  - Verify data exported
  - Verify export file generated
  - Verify user notified

- [ ] **TC-API-071**: POST /api/v1/admin/gdpr/delete/{user_id}
  - Send GDPR deletion request
  - Verify data deleted
  - Verify user notified
  - Verify deletion logged

### 10.14 Admin System Health API
- [ ] **TC-API-072**: GET /api/v1/admin/system/health
  - Send system health request
  - Verify health status returned
  - Verify all services status included
  - Verify response correct

### 10.15 Admin Payment Reconciliation API
- [ ] **TC-API-073**: GET /api/v1/admin/payments/reconciliation
  - Send reconciliation request
  - Verify reconciliation data returned
  - Verify discrepancies identified
  - Verify response correct

### 10.16 Draft Reminders API
- [ ] **TC-API-074**: POST /api/v1/draft-reminders/send
  - Send draft reminders request
  - Verify reminders sent
  - Verify response correct

### 10.17 Fallback Requests API
- [ ] **TC-API-075**: GET /api/v1/admin/fallback-requests
  - Send fallback requests list request
  - Verify requests returned
  - Verify filters work

- [ ] **TC-API-076**: PUT /api/v1/admin/fallback-requests/{request_id}
  - Send fallback request update
  - Verify request updated
  - Verify response correct

### 10.18 Admin Impersonation API
- [ ] **TC-API-077**: POST /api/v1/admin/impersonation/start
  - Send impersonation start request
  - Verify impersonation started
  - Verify token returned
  - Verify impersonation logged

- [ ] **TC-API-078**: POST /api/v1/admin/impersonation/end
  - Send impersonation end request
  - Verify impersonation ended
  - Verify admin session restored

### 10.19 Real-time Data API
- [ ] **TC-API-079**: GET /api/v1/realtime/feeds
  - Send real-time feeds request
  - Verify feeds returned
  - Verify data updates

- [ ] **TC-API-080**: GET /api/v1/data/refresh
  - Send data refresh request
  - Verify refresh initiated
  - Verify status returned

### 10.20 Enhanced Data API
- [ ] **TC-API-081**: GET /api/v1/enhanced-data
  - Send enhanced data request
  - Verify enhanced data returned
  - Verify response correct

### 10.21 Market Data API
- [ ] **TC-API-082**: GET /api/v1/market-data
  - Send market data request
  - Verify market data returned
  - Verify data accurate
  - Verify updates in real-time

### 10.22 Analytics API
- [ ] **TC-API-083**: GET /api/v1/analytics
  - Send analytics request
  - Verify analytics data returned
  - Verify charts data included
  - Verify response correct

### 10.23 API Error Handling
- [ ] **TC-API-084**: Invalid request body
  - Send request with invalid body
  - Verify 400 Bad Request
  - Verify error message

- [ ] **TC-API-085**: Missing required fields
  - Send request missing required fields
  - Verify 422 Validation Error
  - Verify field-level errors

- [ ] **TC-API-086**: Resource not found
  - Send request for non-existent resource
  - Verify 404 Not Found
  - Verify error message

- [ ] **TC-API-087**: Rate limiting
  - Send multiple rapid requests
  - Verify rate limit enforced
  - Verify 429 Too Many Requests

---

## 11. Notification Preferences

### 11.1 User Notification Preferences
- [ ] **TC-NOTIFPREF-001**: View notification preferences
  - Navigate to Account Settings
  - Click "Notification Preferences"
  - Verify all preference options displayed
  - Verify current settings shown

- [ ] **TC-NOTIFPREF-002**: Update email notification preferences
  - Navigate to notification preferences
  - Toggle email notifications on/off
  - Select notification types (report updates, payments, etc.)
  - Save changes
  - Verify preferences saved
  - Verify notifications respect preferences

- [ ] **TC-NOTIFPREF-003**: Update in-app notification preferences
  - Navigate to notification preferences
  - Toggle in-app notifications
  - Select notification types
  - Save changes
  - Verify preferences saved
  - Verify notifications respect preferences

- [ ] **TC-NOTIFPREF-004**: Update notification frequency
  - Navigate to notification preferences
  - Select notification frequency (immediate, daily digest, weekly)
  - Save changes
  - Verify frequency applied
  - Verify notifications sent according to frequency

- [ ] **TC-NOTIFPREF-005**: Test notification preferences
  - Update preferences
  - Trigger notification event
  - Verify notification sent/not sent according to preferences
  - Verify preference enforcement works

---

## 12. Email & Notifications

### 12.1 Email Delivery
- [ ] **TC-EMAIL-001**: Registration email sent
  - Register new user
  - Verify registration email received
  - Verify email content correct
  - Verify email contains verification link

- [ ] **TC-EMAIL-002**: Email verification email
  - Request email verification
  - Verify verification email received
  - Verify email contains verification link
  - Verify link works

- [ ] **TC-EMAIL-003**: Password reset email
  - Request password reset
  - Verify reset email received
  - Verify email contains reset link
  - Verify link works

- [ ] **TC-EMAIL-004**: Welcome email
  - Complete registration
  - Verify welcome email received
  - Verify email content correct

- [ ] **TC-EMAIL-005**: FMV report status emails
  - Report status changes
  - Verify status email sent
  - Verify email content correct
  - Verify email contains report link

- [ ] **TC-EMAIL-006**: FMV report delivered email
  - Report marked as delivered
  - Verify delivery email sent
  - Verify email contains PDF link
  - Verify PDF accessible

- [ ] **TC-EMAIL-007**: Payment confirmation email
  - Payment processed
  - Verify payment email sent
  - Verify email contains receipt
  - Verify receipt information correct

- [ ] **TC-EMAIL-008**: Consultation confirmation email
  - Submit consultation
  - Verify confirmation email sent
  - Verify email content correct

### 12.2 In-App Notifications
- [ ] **TC-NOTIF-001**: Notification created
  - Trigger notification event
  - Verify notification created in database
  - Verify notification appears in UI

- [ ] **TC-NOTIF-002**: Notification displayed
  - Login as user
  - Verify notifications displayed
  - Verify notification count correct

- [ ] **TC-NOTIF-003**: Mark notification as read
  - Click on notification
  - Verify notification marked as read
  - Verify UI updates

- [ ] **TC-NOTIF-004**: Mark all notifications as read
  - Click "Mark all as read"
  - Verify all notifications marked as read
  - Verify UI updates

- [ ] **TC-NOTIF-005**: Notification click navigation
  - Click on notification
  - Verify navigation to relevant page
  - Verify notification marked as read

- [ ] **TC-NOTIF-006**: Notification preferences
  - Navigate to notification preferences
  - Update preferences
  - Verify preferences saved
  - Verify notifications respect preferences

### 12.3 Admin Notifications
- [ ] **TC-NOTIF-007**: Admin notification for new user
  - New user registers
  - Verify admin notified
  - Verify notification appears in admin panel

- [ ] **TC-NOTIF-008**: Admin notification for new report
  - New report submitted
  - Verify admin notified
  - Verify notification appears in admin panel

- [ ] **TC-NOTIF-009**: Admin notification for payment
  - Payment processed
  - Verify admin notified
  - Verify notification appears in admin panel

---

## 13. Data Management & Analytics

### 13.1 Data Display
- [ ] **TC-DATA-001**: Real-time data updates
  - View dashboard
  - Verify data updates in real-time
  - Verify no page refresh required

- [ ] **TC-DATA-002**: Market ticker updates
  - View market ticker
  - Verify ticker updates
  - Verify data accurate

- [ ] **TC-DATA-003**: Live equipment data
  - View equipment data
  - Verify data updates
  - Verify data accurate

### 13.2 Data Export
- [ ] **TC-DATA-004**: Export valuation data
  - Complete valuation
  - Export data
  - Verify export file generated
  - Verify file contains correct data

- [ ] **TC-DATA-005**: Export report data
  - Navigate to reports
  - Export report data
  - Verify export file generated
  - Verify file contains correct data

- [ ] **TC-DATA-006**: Export analytics data
  - Navigate to analytics
  - Export analytics
  - Verify export file generated
  - Verify file contains correct data

### 13.3 Analytics
- [ ] **TC-DATA-007**: View user analytics
  - Navigate to analytics
  - Verify user analytics displayed
  - Verify charts load
  - Verify data accurate

- [ ] **TC-DATA-008**: View revenue analytics
  - Navigate to revenue analytics
  - Verify revenue data displayed
  - Verify charts load
  - Verify data accurate

- [ ] **TC-DATA-009**: View report analytics
  - Navigate to report analytics
  - Verify report statistics displayed
  - Verify data accurate

---

## 14. Security & Compliance

### 14.1 Authentication Security
- [ ] **TC-SEC-001**: Password strength enforcement
  - Attempt weak password
  - Verify password rejected
  - Verify strength requirements displayed

- [ ] **TC-SEC-002**: Account lockout after failed attempts
  - Attempt multiple failed logins
  - Verify account locked
  - Verify lockout message displayed

- [ ] **TC-SEC-003**: Session timeout
  - Login and remain inactive
  - Verify session expires
  - Verify redirect to login

- [ ] **TC-SEC-004**: JWT token security
  - Verify tokens expire correctly
  - Verify tokens cannot be tampered
  - Verify refresh token works

### 14.2 Authorization
- [ ] **TC-SEC-005**: User cannot access admin panel
  - Login as regular user
  - Attempt to access admin URLs
  - Verify access denied
  - Verify redirect to user area

- [ ] **TC-SEC-006**: User cannot access other users' data
  - Login as user A
  - Attempt to access user B's data
  - Verify access denied
  - Verify error message

- [ ] **TC-SEC-007**: Admin can access all areas
  - Login as admin
  - Verify can access all admin areas
  - Verify can access user data

### 14.3 Data Security
- [ ] **TC-SEC-008**: Sensitive data encryption
  - Verify passwords encrypted
  - Verify payment data encrypted
  - Verify PII encrypted

- [ ] **TC-SEC-009**: SQL injection prevention
  - Attempt SQL injection in forms
  - Verify injection prevented
  - Verify error handling

- [ ] **TC-SEC-010**: XSS prevention
  - Attempt XSS in input fields
  - Verify XSS prevented
  - Verify input sanitized

- [ ] **TC-SEC-011**: CSRF protection
  - Attempt CSRF attack
  - Verify CSRF protection active
  - Verify requests rejected

### 14.4 GDPR Compliance
- [ ] **TC-SEC-012**: Data export request
  - User requests data export
  - Verify data exported
  - Verify all user data included
  - Verify data format correct

- [ ] **TC-SEC-013**: Data deletion request
  - User requests data deletion
  - Verify data deleted
  - Verify confirmation sent
  - Verify data cannot be recovered

- [ ] **TC-SEC-014**: Privacy policy accessible
  - Verify privacy policy page accessible
  - Verify policy content displayed
  - Verify policy up to date

---

## 15. Performance & Load Testing

### 15.1 Page Load Performance
- [ ] **TC-PERF-001**: Homepage load time
  - Measure homepage load time
  - Verify load time < 3 seconds
  - Verify all resources load

- [ ] **TC-PERF-002**: Dashboard load time
  - Measure dashboard load time
  - Verify load time < 3 seconds
  - Verify all data loads

- [ ] **TC-PERF-003**: Valuation terminal load time
  - Measure terminal load time
  - Verify load time < 3 seconds
  - Verify all features load

### 15.2 API Performance
- [ ] **TC-PERF-004**: API response times
  - Measure API response times
  - Verify responses < 1 second
  - Verify consistent performance

- [ ] **TC-PERF-005**: Valuation calculation performance
  - Measure valuation calculation time
  - Verify calculation < 5 seconds
  - Verify results accurate

### 15.3 Load Testing
- [ ] **TC-PERF-006**: Concurrent user load
  - Simulate 100 concurrent users
  - Verify system handles load
  - Verify no errors
  - Verify performance acceptable

- [ ] **TC-PERF-007**: Database load
  - Simulate high database load
  - Verify database performance
  - Verify no timeouts

- [ ] **TC-PERF-008**: Payment processing load
  - Simulate multiple concurrent payments
  - Verify payments process correctly
  - Verify no payment failures

---

## 16. Cross-Browser & Responsive Testing

### 16.1 Browser Compatibility
- [ ] **TC-BROWSER-001**: Chrome compatibility
  - Test all features in Chrome
  - Verify all features work
  - Verify no console errors

- [ ] **TC-BROWSER-002**: Firefox compatibility
  - Test all features in Firefox
  - Verify all features work
  - Verify no console errors

- [ ] **TC-BROWSER-003**: Safari compatibility
  - Test all features in Safari
  - Verify all features work
  - Verify no console errors

- [ ] **TC-BROWSER-004**: Edge compatibility
  - Test all features in Edge
  - Verify all features work
  - Verify no console errors

### 16.2 Mobile Responsiveness
- [ ] **TC-RESP-001**: Mobile view (320px)
  - Test on mobile viewport
  - Verify layout responsive
  - Verify all features accessible
  - Verify no horizontal scroll

- [ ] **TC-RESP-002**: Tablet view (768px)
  - Test on tablet viewport
  - Verify layout responsive
  - Verify all features accessible

- [ ] **TC-RESP-003**: Desktop view (1920px)
  - Test on desktop viewport
  - Verify layout optimal
  - Verify all features accessible

### 16.3 Touch Interactions
- [ ] **TC-RESP-004**: Touch navigation
  - Test touch interactions on mobile
  - Verify navigation works
  - Verify buttons tappable
  - Verify forms usable

- [ ] **TC-RESP-005**: Mobile menu
  - Test mobile menu on small screens
  - Verify menu opens/closes
  - Verify menu items accessible

---

## 17. Error Handling & Edge Cases

### 17.1 Form Validation
- [ ] **TC-EDGE-001**: Empty form submission
  - Attempt to submit empty forms
  - Verify validation errors displayed
  - Verify form not submitted

- [ ] **TC-EDGE-002**: Invalid input formats
  - Enter invalid data in forms
  - Verify validation errors
  - Verify helpful error messages

- [ ] **TC-EDGE-003**: Maximum length validation
  - Enter data exceeding max length
  - Verify validation error
  - Verify input truncated or rejected

### 17.2 Network Errors
- [ ] **TC-EDGE-004**: Offline handling
  - Simulate offline condition
  - Verify error message displayed
  - Verify graceful degradation

- [ ] **TC-EDGE-005**: Slow network handling
  - Simulate slow network
  - Verify loading indicators shown
  - Verify timeout handling

- [ ] **TC-EDGE-006**: API error handling
  - Simulate API errors
  - Verify error messages displayed
  - Verify user-friendly messages

### 17.3 Data Edge Cases
- [ ] **TC-EDGE-007**: Empty data sets
  - View pages with no data
  - Verify empty state displayed
  - Verify helpful messages

- [ ] **TC-EDGE-008**: Large data sets
  - View pages with large data
  - Verify pagination works
  - Verify performance acceptable

- [ ] **TC-EDGE-009**: Special characters in input
  - Enter special characters
  - Verify handling correct
  - Verify no errors

### 17.4 File Upload Edge Cases
- [ ] **TC-EDGE-010**: Large file upload
  - Attempt to upload large file
  - Verify file size validation
  - Verify error message if too large

- [ ] **TC-EDGE-011**: Invalid file type
  - Attempt to upload invalid file type
  - Verify file type validation
  - Verify error message

- [ ] **TC-EDGE-012**: Multiple file upload
  - Upload multiple files
  - Verify all files upload
  - Verify files accessible

### 17.5 Payment Edge Cases
- [ ] **TC-EDGE-013**: Payment timeout
  - Simulate payment timeout
  - Verify error handling
  - Verify user can retry

- [ ] **TC-EDGE-014**: Duplicate payment prevention
  - Attempt duplicate payment
  - Verify duplicate prevented
  - Verify error message

- [ ] **TC-EDGE-015**: Partial payment failure
  - Simulate partial payment failure
  - Verify error handling
  - Verify transaction state correct

### 17.6 Real-time Data Edge Cases
- [ ] **TC-EDGE-016**: Market ticker data failure
  - Simulate market data API failure
  - Verify graceful degradation
  - Verify error message displayed
  - Verify fallback data shown

- [ ] **TC-EDGE-017**: Live data update interruption
  - Interrupt live data feed
  - Verify reconnection works
  - Verify data syncs correctly
  - Verify no data loss

### 17.7 Concurrent Operations
- [ ] **TC-EDGE-018**: Concurrent report submissions
  - Submit multiple reports simultaneously
  - Verify all reports processed
  - Verify no data corruption
  - Verify correct status tracking

- [ ] **TC-EDGE-019**: Concurrent payment processing
  - Process multiple payments simultaneously
  - Verify all payments processed correctly
  - Verify no duplicate charges
  - Verify correct status updates

### 17.8 Data Consistency
- [ ] **TC-EDGE-020**: Report status consistency
  - Update report status from multiple sources
  - Verify final status correct
  - Verify no race conditions
  - Verify timeline accurate

- [ ] **TC-EDGE-021**: User data consistency
  - Update user data from multiple sessions
  - Verify final data correct
  - Verify no data loss
  - Verify conflicts resolved

---

## 18. Integration & End-to-End Workflows

### 18.1 Complete User Journey - Spot Check Report
- [ ] **TC-E2E-001**: Complete Spot Check report workflow
  - Register new user
  - Verify email
  - Login
  - Navigate to report generation
  - Select Spot Check tier
  - Fill crane information
  - Submit report request
  - Complete payment
  - Verify report status: Payment Pending → Paid → Submitted
  - Admin processes report
  - Verify status: Submitted → In Review → In Progress → Delivered
  - User receives email notification
  - User downloads PDF
  - Verify complete workflow successful

### 18.2 Complete User Journey - Professional Report
- [ ] **TC-E2E-002**: Complete Professional report workflow
  - Login as existing user
  - Navigate to report generation
  - Select Professional tier
  - Fill detailed crane information
  - Upload service records
  - Submit report request
  - Complete payment ($995)
  - Admin reviews and requests more info
  - User provides additional information
  - Admin completes report
  - User receives and downloads report
  - Verify complete workflow successful

### 18.3 Complete User Journey - Fleet Valuation
- [ ] **TC-E2E-003**: Complete Fleet Valuation workflow
  - Login as user
  - Navigate to fleet valuation
  - Upload CSV file with multiple cranes
  - Verify data imported correctly
  - Edit imported data
  - Submit fleet request
  - Verify fleet price calculated
  - Complete payment
  - Admin processes fleet report
  - User receives fleet report
  - Verify all cranes included
  - Verify complete workflow successful

### 18.4 Complete Valuation Terminal Workflow
- [ ] **TC-E2E-004**: Complete valuation terminal workflow
  - Login as user
  - Navigate to Valuation Terminal
  - Enter crane specifications
  - Calculate standard valuation
  - View results and analysis
  - Save valuation
  - Run enhanced valuation
  - Compare results
  - Export valuation data
  - Verify complete workflow successful

### 18.5 Complete Equipment Management Workflow
- [ ] **TC-E2E-005**: Complete equipment management workflow
  - Login as user
  - Add new equipment
  - Add maintenance records
  - Add inspection records
  - Add valuation records
  - Link equipment to company
  - View equipment statistics
  - Export equipment data
  - Verify complete workflow successful

### 18.6 Complete Admin Workflow - Report Processing
- [ ] **TC-E2E-006**: Complete admin report processing workflow
  - Login as admin
  - View new report in admin panel
  - Review report details
  - Update status to "In Review"
  - Request more information from user
  - User provides information
  - Admin updates status to "In Progress"
  - Admin uploads PDF report
  - Admin marks as "Delivered"
  - Verify user notified
  - Verify email sent with PDF
  - Verify complete workflow successful

### 18.7 Complete Payment & Refund Workflow
- [ ] **TC-E2E-007**: Complete payment and refund workflow
  - User submits report request
  - User completes payment
  - Verify payment processed
  - Verify receipt generated
  - Admin processes refund request
  - Verify refund processed in Stripe
  - Verify user notified
  - Verify refund reflected in user account
  - Verify complete workflow successful

### 18.8 Complete User Registration to First Report
- [ ] **TC-E2E-008**: New user registration to first report
  - Visit homepage
  - Click "Sign Up"
  - Complete registration form
  - Verify email sent
  - Click verification link
  - Login
  - Complete profile setup
  - Navigate to report generation
  - Submit first report
  - Complete payment
  - Verify report submitted
  - Verify welcome email sent
  - Verify onboarding complete

### 18.9 Complete Admin User Management Workflow
- [ ] **TC-E2E-009**: Complete admin user management workflow
  - Login as admin
  - View users list
  - Search for specific user
  - View user details
  - Update user information
  - View user's reports
  - View user's payments
  - Impersonate user (if needed)
  - End impersonation
  - Deactivate user
  - Reactivate user
  - Export user data
  - Verify complete workflow successful

### 18.10 Complete Notification Workflow
- [ ] **TC-E2E-010**: Complete notification workflow
  - User updates notification preferences
  - Report status changes
  - Verify in-app notification created
  - Verify email notification sent (if enabled)
  - User views notification
  - User marks notification as read
  - User marks all as read
  - Verify notification preferences respected
  - Verify complete workflow successful

### 18.11 Complete GDPR Workflow
- [ ] **TC-E2E-011**: Complete GDPR data export workflow
  - User requests data export
  - Admin processes export request
  - Verify data exported
  - Verify user notified
  - User downloads export file
  - Verify all user data included
  - Verify data format correct

- [ ] **TC-E2E-012**: Complete GDPR data deletion workflow
  - User requests data deletion
  - Admin processes deletion request
  - Verify data deleted
  - Verify user notified
  - Verify user cannot login
  - Verify data cannot be recovered
  - Verify deletion logged

### 18.12 Complete Draft Reminder Workflow
- [ ] **TC-E2E-013**: Complete draft reminder workflow
  - User creates draft report
  - Draft remains incomplete for 7+ days
  - Admin runs draft reminder check
  - Verify reminder email sent
  - User receives reminder
  - User completes draft
  - User submits report
  - Verify reminder workflow successful

### 18.13 Complete Overdue Report Workflow
- [ ] **TC-E2E-014**: Complete overdue report workflow
  - Report submitted and paid
  - Report remains in progress beyond SLA
  - Admin runs overdue check
  - Verify overdue report identified
  - Verify alerts sent
  - Admin updates report status
  - Admin completes report
  - Verify overdue workflow successful

### 18.14 Complete Fallback Request Workflow
- [ ] **TC-E2E-015**: Complete fallback request workflow
  - User submits fallback request
  - Verify request created
  - Verify admin notified
  - Admin views fallback request
  - Admin converts to report (if applicable)
  - Admin processes request
  - User receives update
  - Verify fallback workflow successful

### 18.15 Complete Multi-User Concurrent Workflow
- [ ] **TC-E2E-016**: Multiple users concurrent operations
  - Simulate 10 users registering simultaneously
  - Simulate 10 users submitting reports simultaneously
  - Simulate 10 users making payments simultaneously
  - Verify all operations successful
  - Verify no data corruption
  - Verify system performance acceptable
  - Verify all notifications sent correctly

---

## Test Execution Strategy

### Test Priority
1. **Critical (P0)**: Authentication, Payments, FMV Reports, Admin Core Functions
2. **High (P1)**: User Dashboard, Valuation Terminal, Notifications
3. **Medium (P2)**: Analytics, Settings, Content Management
4. **Low (P3)**: Edge Cases, Performance, Cross-Browser

### Test Schedule
- **Daily**: Critical path tests (P0)
- **Weekly**: Full regression suite
- **Pre-Release**: Complete test suite
- **Post-Release**: Smoke tests

### Test Reporting
- Generate test reports after each run
- Track test coverage metrics
- Report bugs with screenshots and logs
- Maintain test execution history

---

## Test Automation Framework Recommendations

### Recommended Tools
- **Playwright** (Recommended) - Cross-browser, fast, reliable
- **Cypress** - Good for frontend testing
- **Selenium** - Mature, widely supported

### Test Structure
```
tests/
├── e2e/
│   ├── auth/
│   ├── dashboard/
│   ├── valuation/
│   ├── fmv-reports/
│   ├── payments/
│   ├── admin/
│   └── api/
├── fixtures/
├── utils/
└── config/
```

### CI/CD Integration
- Run tests on every commit
- Run full suite on pull requests
- Run smoke tests on production deployments

---

## Maintenance & Updates

### Regular Updates
- Update tests when features change
- Add tests for new features
- Remove obsolete tests
- Update test data regularly

### Test Data Management
- Use separate test database
- Reset test data before test runs
- Maintain test user accounts
- Keep test payment methods updated

---

**End of Test Plan**

*This comprehensive test plan covers all aspects of the Crane Intelligence platform. Regular updates should be made as new features are added or existing features are modified.*

