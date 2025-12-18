# Centralized Components Directory

This directory contains all reusable UI components for the Crane Intelligence Platform.

## Components

### 1. `unified-header.html`
Complete header with logo, navigation, authentication UI, and user profile dropdown.

**Usage:**
```html
<div data-component="unified-header"></div>
```

### 2. `unified-footer.html`
Footer with brand info, links, and newsletter subscription.

**Usage:**
```html
<div data-component="unified-footer"></div>
```

### 3. `pricing-section.html`
Terminal Access Plans and Fleet Valuation pricing section.

**Usage:**
```html
<div data-component="pricing-section"></div>
```

### 4. `auth-modals.html`
Login, Signup, and Forgot Password modals.

**Usage:**
```html
<div data-component="auth-modals"></div>
```

### 5. `valuation-form.html`
Crane valuation input form.

**Usage:**
```html
<div data-component="valuation-form"></div>
```

### 6. `payment-module.html`
Stripe payment processing module.

**Usage:**
```html
<div data-component="payment-module" 
     data-amount="999.00" 
     data-service-name="Professional Valuation"
     data-stripe-key="pk_test_...">
</div>
```

## Loading Components

### Automatic Loading
Include the component loader script:
```html
<script src="/js/component-loader.js"></script>
```

Components with `data-component` attributes will be automatically loaded.

### Manual Loading
```javascript
await window.componentLoader.injectComponent('pricing-section', '#pricing-container');
```

## Making Changes

**IMPORTANT:** When updating any component:
1. Edit the component file in `/components/`
2. Changes will automatically reflect on all pages using that component
3. Test on multiple pages to verify consistency

## Dependencies

Components may require:
- `/css/unified-header.css`
- `/js/notification-system.js`
- `/js/unified-auth-utils.js`
- Stripe.js (for payment module)
- Global functions (handlePricingAction, etc.)

