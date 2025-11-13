# Valuation Terminal - Quick Reference Card

## 🚀 Quick Start

**File Location:** `/root/Crane-Intelligence/frontend/valuation_terminal.html`  
**Access URL:** `https://craneintelligence.tech/valuation_terminal.html`  
**File Size:** 95 KB | 2,400 lines

---

## 🔧 Core Functions

### Tab Management
```javascript
switchTab(tab, element)    // Main tab switching (Single/Bulk)
switchAnalysis(analysis, element)  // Analysis tab switching
```

**Usage:**
```html
<button onclick="switchTab('single', this)">Single Valuation</button>
<button onclick="switchAnalysis('costbreakdown', this)">Cost Breakdown</button>
```

### Chart Management
```javascript
initializeTrendChart()         // Overview trend chart
initializeManufacturerChart()  // Manufacturer distribution
initializeCapacityChart()      // Capacity analysis
```

**Note:** All charts auto-destroy previous instances to prevent memory leaks.

---

## 📊 Features Overview

### 1. Single Valuation
- Form fields: Manufacturer, Model, Year, Capacity, Hours, Region
- Sample data loader
- Real-time calculation
- Results with confidence score

### 2. Bulk Processing
- Drag & drop Excel upload
- CSV/XLSX support
- Batch processing
- Export results

### 3. Analysis Tabs
1. **Overview** - Trend chart + key metrics
2. **Analysis** - Manufacturer & capacity charts
3. **Cost Breakdown** - Detailed calculation breakdown ✨ NEW
4. **Comparables** - Market sales data
5. **Risk** - Risk assessment matrix

### 4. Quick Actions Tools
- **Notes** - Save/load from localStorage
- **Calendar** - Event scheduling
- **Unit Converter** - Real-time conversion

---

## 🎨 Design System

### Colors
- Primary: `#00FF88` (Green)
- Background: `#0F0F0F` (Dark)
- Cards: `#1A1A1A`
- Borders: `#404040`
- Text: `#FFFFFF`
- Warning: `#FFB800`
- Error: `#FF4444`

### Fonts
- Display: JetBrains Mono
- Body: Inter
- Code: JetBrains Mono

---

## 🔍 Troubleshooting

### Issue: Tabs not switching
**Solution:** Verify onclick handlers include `this`:
```html
<button onclick="switchTab('bulk', this)">Bulk</button>
```

### Issue: Charts not rendering
**Solution:** Check Chart.js CDN is loaded:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Issue: Mobile layout broken
**Solution:** Responsive breakpoint is 768px:
```css
@media (max-width: 768px) { ... }
```

### Issue: Notes not saving
**Solution:** Check localStorage is enabled in browser

---

## 📱 Responsive Breakpoints

| Screen Size | Layout |
|-------------|--------|
| > 768px | Desktop - Multi-column grid |
| ≤ 768px | Mobile - Single column |

---

## ⚡ Performance Tips

1. Charts are lazy-loaded (only on tab activation)
2. Chart instances are reused (memory efficient)
3. localStorage for persistent data
4. Optimized CSS selectors
5. Debounced input events

---

## 🐛 Known Limitations

- Maximum file size for bulk upload: 10MB
- Bulk processing limited to 1000 rows
- Chart animations may lag on old devices
- localStorage has 5-10MB limit (browser dependent)

---

## 📝 Quick Fixes

### Clear All Data
```javascript
localStorage.removeItem('valuationNotes');
```

### Reset Charts
```javascript
Object.values(chartInstances).forEach(chart => chart.destroy());
chartInstances = {};
```

### Force Refresh
```javascript
location.reload(true);
```

---

## 🔗 Dependencies

- Chart.js v4.x (CDN)
- XLSX v0.18.5 (CDN)
- Google Fonts (Inter, JetBrains Mono)

---

## 📞 Support

For issues, check:
1. Browser console for errors
2. Network tab for failed requests
3. VALUATION_TERMINAL_FIX_SUMMARY.md for details

---

**Last Updated:** October 8, 2025  
**Version:** 2.0 (Optimized)

