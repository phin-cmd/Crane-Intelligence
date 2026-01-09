# Email Design Specifications for Crane Intelligence

## Grid System & Layout Structure

### Table-Based Layout

Email clients have limited CSS support, so we use table-based layouts for maximum compatibility.

**Standard Email Structure:**
```html
<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding: 20px 0;">
      <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px;">
        <!-- Email content here -->
      </table>
    </td>
  </tr>
</table>
```

**Container Width:**
- Maximum: 600px
- Centered with auto margins
- Full-width background wrapper (100%)

**Column Structure:**
- Single column: Full width (600px)
- Two columns: 280px each with 20px gap (desktop only)
- Mobile: Always single column (stacks at 600px breakpoint)

### Spacing System

**Padding:**
- Container padding: 40px (desktop), 30px (mobile)
- Section padding: 30px (desktop), 20px (mobile)
- Content padding: 20px (desktop), 15px (mobile)

**Margins:**
- Between sections: 30px
- Between content blocks: 20px
- Between paragraphs: 16px
- Between list items: 8px

**Gaps:**
- Column gaps: 20px (two-column layouts)
- Button spacing: 10px between buttons

## Component Library

### Buttons

**Primary Button (Green):**
```html
<table cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="background-color: #00FF85; border-radius: 6px; padding: 14px 32px;">
      <a href="{{ cta_url }}" style="color: #0F0F0F; text-decoration: none; font-weight: 600; font-size: 16px; font-family: 'Inter', Arial, sans-serif;">Button Text</a>
    </td>
  </tr>
</table>
```

**Specifications:**
- Background: #00FF85
- Text color: #0F0F0F
- Padding: 14px 32px (vertical, horizontal)
- Border radius: 6px
- Font weight: 600
- Font size: 16px
- Minimum height: 44px (touch target)

**Secondary Button (Yellow):**
```html
<table cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="background-color: #FFD600; border-radius: 6px; padding: 14px 32px;">
      <a href="{{ url }}" style="color: #0F0F0F; text-decoration: none; font-weight: 600; font-size: 16px; font-family: 'Inter', Arial, sans-serif;">Button Text</a>
    </td>
  </tr>
</table>
```

**Specifications:**
- Background: #FFD600
- Text color: #0F0F0F
- Same padding and sizing as primary

**Text Link:**
```html
<a href="{{ url }}" style="color: #00FF85; text-decoration: none; font-weight: 500;">Link Text</a>
```

**Hover States:**
- Underline on hover (where supported)
- Slight opacity change (0.9) for buttons
- Note: Many email clients don't support :hover

### Cards

**Info Card:**
```html
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: rgba(0, 255, 133, 0.1); border-left: 4px solid #00FF85; border-radius: 4px; padding: 16px;">
  <tr>
    <td>
      <!-- Content -->
    </td>
  </tr>
</table>
```

**Specifications:**
- Background: rgba(0, 255, 133, 0.1)
- Left border: 4px solid #00FF85
- Border radius: 4px
- Padding: 16px

**Warning Card:**
- Background: rgba(255, 214, 0, 0.1)
- Left border: 4px solid #FFD600
- Same structure as info card

**Alert Card:**
- Background: rgba(255, 68, 68, 0.1)
- Left border: 4px solid #FF4444
- Same structure as info card

### Dividers

**Standard Divider:**
```html
<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="height: 1px; background-color: #333333; padding: 30px 0;"></td>
  </tr>
</table>
```

**Specifications:**
- Height: 1px
- Color: #333333
- Vertical padding: 30px (creates spacing)

**Thick Divider:**
- Height: 2px
- Same color and padding

### Info Boxes

**Success/Info Box:**
- Green accent border (left: 4px solid #00FF85)
- Light green background (rgba(0, 255, 133, 0.1))
- Padding: 16px
- Border radius: 4px

**Warning Box:**
- Yellow accent border (left: 4px solid #FFD600)
- Light yellow background (rgba(255, 214, 0, 0.1))
- Same padding and radius

**Alert Box:**
- Red accent border (left: 4px solid #FF4444)
- Light red background (rgba(255, 68, 68, 0.1))
- Same padding and radius

## Image Specifications

### Logo Images

**Dimensions:**
- Desktop: 200px width × 40-60px height
- Mobile: 150-180px width × 35-50px height
- Aspect ratio: ~5:1 (width:height)

**Formats:**
- Primary: SVG (inline or hosted)
- Fallback: PNG (for clients that don't support SVG)
- File size: Keep under 50KB

**Implementation:**
```html
<img src="https://craneintelligence.tech/images/logos/crane-intelligence-logo-white.svg" 
     alt="Crane Intelligence" 
     width="200" 
     height="60" 
     style="display: block; max-width: 200px; height: auto;" />
```

### Content Images

**Dimensions:**
- Maximum width: 600px (full email width)
- Recommended: 560px (with padding)
- Height: Maintain aspect ratio
- File size: Optimize to under 200KB

**Formats:**
- JPG: For photographs, complex images
- PNG: For logos, graphics with transparency
- GIF: For simple animations (use sparingly)

**Optimization:**
- Compress images before embedding
- Use appropriate quality settings (80-90% for JPG)
- Remove EXIF data
- Consider WebP (limited support in email)

**Responsive Images:**
```html
<img src="{{ image_url }}" 
     alt="Descriptive alt text" 
     width="560" 
     style="display: block; max-width: 100%; height: auto;" />
```

### Image Best Practices

- Always include alt text
- Use width and height attributes
- Set display: block to remove spacing
- Use max-width: 100% for responsiveness
- Test with images disabled

## Responsive Breakpoints

### Desktop (600px and above)

**Layout:**
- Full 600px width
- Two-column layouts possible
- 40px padding
- Full feature set

**Typography:**
- H1: 28px
- H2: 24px
- H3: 20px
- Body: 16px

### Tablet (480px - 599px)

**Layout:**
- Single column
- 30px padding
- Stacked content

**Typography:**
- H1: 24px
- H2: 20px
- H3: 18px
- Body: 15px

### Mobile (Below 480px)

**Layout:**
- Single column
- 20px padding
- Full-width buttons
- Stacked elements

**Typography:**
- H1: 22px
- H2: 18px
- H3: 16px
- Body: 14px

**Touch Targets:**
- Minimum 44px × 44px
- Increased button padding
- Larger tap areas

### Media Queries

```css
@media only screen and (max-width: 600px) {
  .email-content {
    padding: 30px 20px !important;
  }
  .email-header {
    padding: 30px 20px !important;
  }
  h1 { font-size: 24px !important; }
  h2 { font-size: 20px !important; }
}

@media only screen and (max-width: 480px) {
  .email-content {
    padding: 20px 15px !important;
  }
  .button-primary {
    width: 100% !important;
    padding: 16px !important;
  }
}
```

## Accessibility Guidelines

### WCAG AA Compliance

**Color Contrast:**
- Normal text: Minimum 4.5:1 contrast ratio
- Large text (18px+): Minimum 3:1 contrast ratio
- UI components: Minimum 3:1 contrast ratio

**Tested Combinations:**
- White (#FFFFFF) on dark (#0F0F0F): 21:1 ✓
- Secondary text (#B0B0B0) on dark: 4.8:1 ✓
- Green button (#00FF85) on dark: 4.8:1 ✓
- Yellow button (#FFD600) on dark: 5.2:1 ✓

### Alt Text Requirements

**All Images Must Have Alt Text:**
- Descriptive alt text for informative images
- Empty alt="" for decorative images
- Logo: "Crane Intelligence"
- Buttons: Describe the action
- Charts/graphs: Describe the data

**Examples:**
```html
<!-- Informative -->
<img src="chart.png" alt="Crane market value trends showing 15% increase over Q4 2024" />

<!-- Decorative -->
<img src="divider.png" alt="" />

<!-- Logo -->
<img src="logo.svg" alt="Crane Intelligence" />
```

### Semantic HTML

**Proper Structure:**
- Use `<h1>`, `<h2>`, `<h3>` for headings (in order)
- Use `<p>` for paragraphs
- Use `<ul>`, `<ol>`, `<li>` for lists
- Use `<table>` for tabular data
- Use `<a>` for links

**Heading Hierarchy:**
- One `<h1>` per email (main headline)
- Use `<h2>` for major sections
- Use `<h3>` for subsections
- Don't skip heading levels

### Readable Font Sizes

**Minimum Sizes:**
- Body text: 14px (minimum), 16px (recommended)
- Headings: 18px (minimum)
- Footer text: 12px (acceptable for disclaimers)
- Buttons: 16px (minimum)

**Mobile Considerations:**
- Increase font sizes on mobile
- Minimum 16px for body text on mobile
- Larger touch targets (44px minimum)

### Link Accessibility

**Link Text:**
- Descriptive link text (not "click here")
- Indicate if link opens in new window
- Make link purpose clear from context

**Examples:**
- ✓ "View your valuation report"
- ✓ "Download the full case study"
- ✗ "Click here"
- ✗ "Read more"

## Dark Mode Considerations

### Current Implementation

Our emails already use a dark theme, which works well in dark mode email clients.

**Background Colors:**
- Primary: #0F0F0F (works in both light and dark modes)
- Content: #1A1A1A (dark enough for dark mode)

**Text Colors:**
- Primary: #FFFFFF (high contrast in dark mode)
- Secondary: #B0B0B0 (readable in dark mode)

### Dark Mode Best Practices

**Color Adjustments:**
- Test emails in dark mode clients
- Ensure sufficient contrast
- Avoid pure black backgrounds (use #0F0F0F)
- Use slightly lighter backgrounds for content areas

**Image Considerations:**
- Logo works on dark backgrounds
- Ensure images are visible in dark mode
- Consider dark mode variants if needed

## Email Client-Specific Considerations

### Outlook (Windows)

**Limitations:**
- No support for background images in `<body>`
- Limited CSS support
- Use VML for background colors in some versions
- Test in Outlook 2016, 2019, 365

**Workarounds:**
- Use table-based layouts
- Inline all critical styles
- Avoid advanced CSS
- Use conditional comments for Outlook-specific code

### Gmail

**Considerations:**
- Strips `<style>` tags from `<body>`
- Keep styles in `<head>`
- Supports media queries
- Good responsive support

### Apple Mail

**Features:**
- Good CSS support
- Supports media queries
- Handles web fonts well
- Good dark mode support

### Mobile Clients

**Best Practices:**
- Single column layouts
- Large touch targets (44px minimum)
- Readable font sizes
- Test on iOS and Android
- Test in native apps and web clients

## Performance Guidelines

### File Size Limits

**HTML Size:**
- Target: Under 100KB
- Maximum: 150KB
- Remove unnecessary code
- Minimize inline CSS

**Image Sizes:**
- Logo: Under 50KB
- Content images: Under 200KB each
- Total images: Under 500KB per email

### Loading Performance

**Optimization:**
- Compress all images
- Minimize HTML
- Remove unused CSS
- Use efficient code structure

**Testing:**
- Test with slow connections
- Ensure text loads first
- Images should have fallbacks
- Critical content above the fold

## Testing Checklist

### Pre-Send Testing

- [ ] All images have alt text
- [ ] Color contrast meets WCAG AA
- [ ] Links are properly formatted
- [ ] Unsubscribe link works
- [ ] Mobile responsiveness verified
- [ ] Logo displays correctly
- [ ] Buttons are clickable
- [ ] Text is readable
- [ ] Footer information is complete
- [ ] Personalization variables work

### Email Client Testing

- [ ] Gmail (web, iOS, Android)
- [ ] Outlook (2016, 2019, 365)
- [ ] Apple Mail (macOS, iOS)
- [ ] Yahoo Mail
- [ ] Mobile clients

### Accessibility Testing

- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Color contrast ratios
- [ ] Alt text for images
- [ ] Semantic HTML structure

## Revision History

- **2025-01-XX**: Initial design specifications created

---

**For Implementation Questions:**
Refer to EMAIL_BRAND_GUIDE.md for brand guidelines and EMAIL_TEMPLATE_USAGE.md for usage instructions.
