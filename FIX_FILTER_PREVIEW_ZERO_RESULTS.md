# Fix for Filter Preview Returning 0 Results

## Problem

When adding a location filter (Country: United States) and clicking "Preview Filter Impact", the segment drops from 2,998 → 0 customers (-100%).

## Root Cause

**Data/UI Mismatch!**

- **Generated Data:** Uses `"USA"` as country value
- **UI Dropdown:** Shows `"United States"`, `"United Kingdom"`, etc.
- **Result:** Filter searches for "United States" but data only has "USA" → 0 matches!

### Evidence from Data Generation:

```python
# scripts/generate_data.py line 69-75
self.cities = [
    ('New York', 'USA'),      # ← Uses "USA"
    ('Los Angeles', 'USA'),   # ← Not "United States"
    ('Chicago', 'USA'),
    ...
]
```

## Solution

### 1. **Updated UI Dropdown to Match Data** ✅

**File:** `frontend/index.html`

**Before:**
```html
<select id="filter-country" class="filter-input">
    <option value="">All Countries</option>
    <option value="United States">United States</option>
    <option value="United Kingdom">United Kingdom</option>
    <option value="Canada">Canada</option>
    <option value="Australia">Australia</option>
</select>
```

**After:**
```html
<select id="filter-country" class="filter-input">
    <option value="">All Countries</option>
    <option value="USA">USA</option>
</select>
```

### 2. **Why This Happens**

The synthetic data only generates USA locations:
- New York, USA
- Los Angeles, USA
- Chicago, USA
- Houston, USA
- Phoenix, USA
- Philadelphia, USA
- San Antonio, USA
- San Diego, USA
- Dallas, USA
- San Jose, USA
- Austin, USA
- Seattle, USA
- Denver, USA
- Boston, USA
- Miami, USA

**All cities are in the USA!**

## Testing

### 1. **Refresh Your Browser**
```
Press Ctrl+F5 (hard refresh)
```

### 2. **Try Filter Preview Again**

1. Go to Step 3: Refine Segment
2. Select Country: **USA** (not "United States")
3. Click "Preview Filter Impact"

**Expected Result:**
```
Starting Size: 2,998
After Filters: ~2,998
Percentage retained: ~100%
```

Since all customers are in the USA, the filter should keep them all!

### 3. **Try City Filter**

Enter a specific city like:
- "New York"
- "Los Angeles"  
- "Chicago"

**Expected Result:**
```
Starting Size: 2,998
After Filters: ~200-300
Percentage retained: ~10%
```

Each city should have roughly 1/15th of customers.

## Alternative: Expand Data to Include More Countries

If you want to support multiple countries, update the data generation:

**File:** `scripts/generate_data.py`

```python
self.cities = [
    # USA
    ('New York', 'United States'), ('Los Angeles', 'United States'),
    ('Chicago', 'United States'), ('Houston', 'United States'),
    
    # UK
    ('London', 'United Kingdom'), ('Manchester', 'United Kingdom'),
    ('Birmingham', 'United Kingdom'),
    
    # Canada
    ('Toronto', 'Canada'), ('Vancouver', 'Canada'),
    ('Montreal', 'Canada'),
    
    # Australia
    ('Sydney', 'Australia'), ('Melbourne', 'Australia'),
    ('Brisbane', 'Australia'),
]
```

Then regenerate data:
```powershell
.\venv\Scripts\Activate.ps1
python scripts\generate_data.py
```

And update the UI dropdown back to:
```html
<option value="United States">United States</option>
<option value="United Kingdom">United Kingdom</option>
<option value="Canada">Canada</option>
<option value="Australia">Australia</option>
```

## Current State

✅ **Fixed for Current Data:** Dropdown now shows "USA" which matches the data  
⚠️ **Limitation:** Only USA is available (all synthetic data is USA-based)  
💡 **Future:** Can expand data generation to include multiple countries  

## Verification

After refreshing, try these filter combinations:

**Test 1: Country USA Only**
- Country: USA
- Expected: ~100% retained (all customers are in USA)

**Test 2: City Filter**
- Country: USA
- City: New York
- Expected: ~5-10% retained (1 city out of 15)

**Test 3: Combined Filters**
- Country: USA
- City: New York
- CLV Min: 80%
- Expected: ~1-2% retained (high-value New Yorkers)

---

**Refresh your browser (Ctrl+F5) and test with Country: USA!** 🎯

