# Fix for "invalid literal for int() with base 10: 'limited'" Error

## Problem

The backend was crashing with:
```
invalid literal for int() with base 10: 'limited'
```

This happened when Gemini returned a non-numeric string (like `"limited"`) for the `metric_target.value` field, which should be a number like `0.2` for 20%.

## Root Cause

In `backend/models/intent_interpreter.py`, the code was doing:
```python
metric_value = metric_data.get('value', 0.1)
value=float(metric_value)  # CRASH if metric_value is "limited"
```

If Gemini returned `{"metric_target": {"value": "limited"}}`, the `float()` conversion would fail.

## Solutions Applied

### 1. Robust Error Handling (Immediate Fix ✅)

Added comprehensive error handling in `_parse_to_coo()`:

```python
# Try to convert to float, handle non-numeric strings
try:
    if raw_value is None:
        metric_value = 0.1
    elif isinstance(raw_value, (int, float)):
        metric_value = float(raw_value)
    elif isinstance(raw_value, str):
        # Handle percentage strings like "20%" or "20 percent"
        if '%' in cleaned or 'percent' in cleaned:
            cleaned = cleaned.replace('%', '').replace('percent', '').strip()
            metric_value = float(cleaned) / 100  # Convert to decimal
        else:
            # Try direct conversion
            metric_value = float(cleaned)
    else:
        metric_value = 0.1
except (ValueError, TypeError) as e:
    print(f"Warning: Could not parse metric value '{raw_value}': {e}")
    print(f"Using default value: 0.1")
    metric_value = 0.1
```

**This handles:**
- `None` values
- Numeric values (int or float)
- Percentage strings ("20%", "20 percent")
- Invalid strings (fallback to 0.1)
- Any other parsing errors

### 2. Improved Gemini Prompt (Prevents Future Issues ✅)

Updated the prompt to be more explicit:

```python
IMPORTANT: 
- metric_target.value MUST be a numeric decimal (0.20 for 20%, 0.15 for 15%, etc.)
- target_behavior should use underscore_case (e.g., abandoned_cart, not "cart abandonment")
- All field names must match exactly as shown above
```

**Benefits:**
- Clearer instructions for Gemini
- Example values in the JSON structure
- Explicit format requirements

### 3. Better Field Name Guidance

Added explicit instructions about `target_behavior` naming:
- ✅ Use: `abandoned_cart` (underscore_case)
- ❌ Avoid: `"cart abandonment"` (natural language)

This helps ensure AI filters can match properly!

## Expected Behavior After Fix

### Before:
```
❌ Backend crashes with "invalid literal for int()"
❌ Campaign analysis fails
❌ Frontend shows "Analysis failed" error
```

### After:
```
✅ Non-numeric values handled gracefully
✅ Warning logged but processing continues
✅ Default value (0.1) used if parsing fails
✅ Campaign analysis completes successfully
```

## Testing

1. **Restart your backend:**
   ```powershell
   python run.py
   ```

2. **Try your campaign analysis again** in the browser

3. **Check backend logs for:**
   ```
   🎯 Campaign Objective Object:
      Goal: conversion
      Target Behavior: abandoned_cart  ← Should be underscore_case now
      Target Subgroup: high_value_shopper
   
   🔍 Extracting AI Filters...
      target_behavior: 'abandoned_cart'  ← Should match!
      ✓ Is abandoned_cart - adding behavior filter
      📝 Total AI filters extracted: 4
   ```

## What to Expect Now

1. **Error will not crash the backend** - it logs a warning and continues
2. **Gemini should return better values** - more explicit prompt
3. **AI filters should extract** - if target_behavior uses underscore_case
4. **Segment size should be correct** - filtered by the criteria

## Still Having Issues?

If you still see problems, share the backend terminal output showing:
- 🎯 Campaign Objective Object (especially `target_behavior`)
- 🔍 Extracting AI Filters section
- Any ⚠️ warnings about parsing

This will help us debug what Gemini is actually returning!

---

**Restart the backend now and try again - the crash should be fixed!** 🚀

