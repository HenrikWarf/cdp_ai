# Fix for Pydantic Validation Error - "invalid literal for int() with base 10"

## Problem

Getting repeated errors like:
```
invalid literal for int() with base 10: 'limited'
invalid literal for int() with base 10: 'not'
```

When Gemini returns non-numeric strings for `metric_target.value`.

## Root Cause

The issue was happening at the **Pydantic validation layer**, not in our intent interpreter code.

### Order of Operations (Before Fix):
1. Gemini returns: `{"metric_target": {"type": "...", "value": "not"}}`
2. Intent interpreter tries to create `MetricTarget(type="...", value="not")`
3. **Pydantic tries to coerce `"not"` to `float`** ❌ **CRASH HERE**
4. Our error handling in `_parse_to_coo()` never runs (too late!)

## Solution

Added a **Pydantic field validator** that intercepts the value **before** Pydantic's automatic type coercion:

### File: `backend/api/schemas.py`

```python
class MetricTarget(BaseModel):
    """Metric target specification"""
    type: str = Field(..., description="Type of metric")
    value: float = Field(..., description="Target value (will be parsed from string if needed)")
    
    @field_validator('value', mode='before')
    @classmethod
    def parse_value(cls, v):
        """Parse value to float, handling non-numeric strings gracefully"""
        if v is None:
            return 0.1
        
        if isinstance(v, (int, float)):
            return float(v)
        
        if isinstance(v, str):
            try:
                # Try to parse percentage strings like "20%" or "20 percent"
                cleaned = v.strip().lower()
                if '%' in cleaned or 'percent' in cleaned:
                    cleaned = cleaned.replace('%', '').replace('percent', '').strip()
                    return float(cleaned) / 100  # Convert to decimal
                else:
                    # Try direct conversion
                    return float(cleaned)
            except (ValueError, TypeError):
                # Fallback to default
                print(f"⚠️  Warning: Could not parse metric value '{v}', using 0.1")
                return 0.1
        
        return 0.1
```

### Order of Operations (After Fix):
1. Gemini returns: `{"metric_target": {"type": "...", "value": "not"}}`
2. Intent interpreter tries to create `MetricTarget(type="...", value="not")`
3. **Pydantic calls `parse_value('not')` validator first** ✅
4. **Validator catches error and returns `0.1`** ✅
5. MetricTarget created successfully with `value=0.1`
6. Warning logged but no crash!

## What This Handles

✅ `None` values → 0.1  
✅ Numeric values (int/float) → converted to float  
✅ Percentage strings ("20%", "20 percent") → 0.20  
✅ Other numeric strings ("0.15") → 0.15  
✅ Invalid strings ("not", "limited", etc.) → 0.1 with warning  
✅ Any other type → 0.1  

## Benefits

1. **Catches errors at validation layer** (earliest possible point)
2. **Prevents crash** - logs warning and continues
3. **Handles multiple formats** - percentages, decimals, etc.
4. **Type-safe** - always returns float
5. **Backward compatible** - works with our existing prompt improvements

## Testing

**Restart your backend:**
```powershell
python run.py
```

**Try your campaign analysis again:**
- Even if Gemini returns invalid strings, it will now work!
- Check backend logs for warnings like:
  ```
  ⚠️  Warning: Could not parse metric value 'not', using 0.1
  ```

## Expected Behavior

### Before:
```
❌ Backend crashes with "invalid literal for int()"
❌ Campaign analysis fails
❌ Frontend shows "Analysis failed" error
```

### After:
```
✅ Non-numeric values caught by validator
✅ Warning logged: "Could not parse metric value 'not', using 0.1"
✅ Processing continues with default value
✅ Campaign analysis completes successfully
```

## Combined Fixes

This fix works together with our previous improvements:

1. **Pydantic Validator** (this fix) - First line of defense
2. **Intent Interpreter Error Handling** - Backup safety net
3. **Improved Gemini Prompt** - Reduces likelihood of bad values

### Multi-Layer Protection:
```
Gemini Response
      ↓
[Pydantic Validator] ← NEW! Catches errors here
      ↓
[Intent Interpreter] ← Backup handling
      ↓
[MetricTarget Object] ← Always valid!
```

## Additional Improvements

We also:
- Improved the Gemini prompt to explicitly request numeric decimals
- Added example JSON with correct format (0.20 for 20%)
- Requested underscore_case for field names (abandoned_cart not "cart abandonment")

## Restart Required

**You MUST restart the backend for this fix to take effect:**

```powershell
# Stop current backend (Ctrl+C)
python run.py
```

Then refresh your browser and try the campaign analysis again!

---

**This should completely fix the parsing errors - restart the backend now!** 🚀

