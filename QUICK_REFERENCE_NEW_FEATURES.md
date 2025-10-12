# Quick Reference: New Valuation Terminal Features

## 🆕 New Form Fields

### Crane Type (Required)
**Location:** Third row, first field  
**Options:**
- Crawler Crane
- All-Terrain Crane
- Rough Terrain Crane
- Truck-Mounted Crane
- Telescopic Crawler Crane

**Purpose:** Ensures accurate comparable sales matching

---

### Boom Length (Optional)
**Location:** Third row, second field  
**Input:** Number in feet  
**Example:** 350  
**Premium:** $500 per foot over 300ft

---

### Jib Included (Optional)
**Location:** Fourth row, first field  
**Options:**
- No (default)
- Yes - Standard Jib
- Yes - Luffing Jib

**Premiums:**
- Standard Jib: $50,000 base + $400/ft
- Luffing Jib: $150,000 base + $800/ft
- Special models with luffing jib: Additional $150,000

---

### Jib Length (Optional)
**Location:** Fourth row, second field  
**Input:** Number in feet  
**Example:** 120  
**Note:** Only applies if jib is included

---

## 📊 New Analysis Tab: Rental vs Purchase

### Features:
1. **Monthly Rental Rate**
   - Calculated at 1.5% of crane value
   - Example: $1.1M crane = $16,500/month

2. **Annual Rental Revenue**
   - Monthly rate × 12
   - Shows potential revenue if renting out

3. **5-Year Cost Comparison**
   - Purchase scenario (includes operating costs)
   - Rental scenario (monthly rate × 60 months)
   - Break-even point analysis

4. **Operating Costs Included:**
   - Maintenance: 3% of value/year
   - Insurance: 1.5% of value/year
   - Storage: $12,000/year

---

## 🔍 Improved Comparables

### Filtering Logic:
- **Exact crane type match** (no mixing classes)
- **Capacity range:** ±30% of target
- **Maximum results:** 4 most relevant comparables

### Example:
**Input:** 110T Crawler Crane  
**Shows:** Only 77-143T Crawler Cranes  
**Won't Show:** All-terrain, truck-mounted, or wrong capacity crawlers

---

## 🏢 Updated Manufacturers

### Removed (Defunct):
- ❌ American
- ❌ Demag
- ❌ Galleon
- ❌ Manitex
- ❌ Shuttle lift

### Active Manufacturers:
- ✅ Liebherr
- ✅ Tadano
- ✅ Grove
- ✅ Manitowoc
- ✅ Link-Belt
- ✅ Sany
- ✅ XCMG
- ✅ Kobelco
- ✅ Terex
- ✅ Zoomlion
- ✅ HSC
- ✅ Kato
- ✅ IHI

---

## 💡 Sample Data (Updated)

Click "LOAD SAMPLE DATA" to populate with:
- **Manufacturer:** Kobelco
- **Model:** CK1100G-2
- **Year:** 2018
- **Capacity:** 110 tons
- **Hours:** 5,000
- **Crane Type:** Crawler Crane
- **Boom Length:** 350 ft
- **Jib:** Luffing Jib
- **Jib Length:** 120 ft
- **Region:** North America

---

## 🧮 Calculation Formulas

### Base Value
```
baseValue = capacity × $5,000/ton
```

### Boom Premium
```
boomPremium = 0 (if ≤300ft)
boomPremium = (length - 300) × $500 (if >300ft)
```

### Standard Jib Premium
```
jibPremium = $50,000 + (jibLength × $400)
```

### Luffing Jib Premium
```
luffingPremium = $150,000 + (jibLength × $800)
+ $150,000 if premium model (LR1300, LR1600, CK1100, CK1200)
```

### Rental Rate
```
monthlyRental = estimatedValue × 0.015 (1.5%)
```

### 5-Year Purchase Cost
```
purchase = craneValue
maintenance = craneValue × 0.03 × 5
insurance = craneValue × 0.015 × 5
storage = $12,000 × 5
total = purchase + maintenance + insurance + storage
```

### 5-Year Rental Cost
```
rentalCost = monthlyRental × 60 months
```

---

## 🎯 Use Cases

### Case 1: High-Value Crawler with Luffing Jib
**Best For:** Liebherr LR1300SX, Kobelco CK1100G+  
**Impact:** Adds $250,000-$450,000 to valuation  
**Why:** Luffing jibs are highly specialized and valuable

### Case 2: Standard Crane Without Special Equipment
**Best For:** Most all-terrain and rough terrain cranes  
**Impact:** Standard depreciation and rental calculations  
**Why:** Straightforward valuation without premiums

### Case 3: Rental Analysis
**Best For:** Fleet operators deciding purchase vs lease  
**Shows:** 
- Break-even point (typically 3-7 years)
- Monthly cash flow requirements
- Long-term cost comparison

---

## ⚠️ Important Notes

1. **Always Select Crane Type:** Required for accurate comparables
2. **Boom Package Matters:** Can add $300k+ to valuation
3. **Rental Rate Standard:** Industry standard is 1.5% of value
4. **Comparables Quality:** Now filtered to ensure relevance
5. **Operating Costs:** Included in 5-year analysis (maintenance, insurance, storage)

---

## 🐛 Debugging

All calculations are logged to browser console:
```javascript
console.log('Crane Valuation Summary:');
console.log('Estimated Value:', '$X,XXX,XXX');
console.log('Monthly Rental Rate (1.5%):', '$XX,XXX');
console.log('Boom Package Premium:', '$XXX,XXX');
```

Open browser developer tools (F12) to view detailed calculations.

---

## 📞 Next Steps

1. Test the new form fields with various crane configurations
2. Verify rental rates match expectations (1.5% of value)
3. Check that comparables show only relevant crane classes
4. Review 5-year cost analysis for reasonableness
5. Confirm boom package premiums calculate correctly

---

**Last Updated:** October 10, 2025  
**Version:** 2.0 - Major Valuation Logic Update

