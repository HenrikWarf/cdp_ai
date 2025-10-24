# Troubleshooting: Segment Size Showing 0

## Problem

After implementing the three-section refinement UI with AI filters, the segment size is showing 0 in the frontend, and calculated values are not appearing correctly.

## Diagnosis Steps

### Step 1: Run the Test Script

```bash
python test_backend.py
```

This will:
- Test the health endpoint
- Test the campaign analysis endpoint
- Save the response to `test_response.json`
- Show you the segment size and AI filters in the response

**Look for:**
- ✅ HTTP 200 status
- ✅ `estimated_size` > 0
- ✅ `ai_filters` array present
- ❌ Any error messages

### Step 2: Check Backend Terminal Logs

When you run a campaign analysis, you should see these logs in the backend terminal:

```
📊 Fetching full segment data...
🔍 Query Preview:
   SELECT c.customer_id, c.email_address, ...

✅ Query executed successfully!
   Total customers in segment: 1234

📊 Calculating segment metadata...
   Customer DataFrame shape: (1234, 15)
   Columns: ['customer_id', 'email_address', ...]
   Segment ID: SEG_PERS_DISC_ABC123
   Estimated size: 1234
   AI Filters extracted: 4
   Creating SegmentMetadata with ai_filters: 4
   ✅ SegmentMetadata created successfully

🎯 Creating CampaignAnalysisResponse...
   Segment preview size: 1234
   Trigger suggestions: 5
   AI filters: 4
   ✅ CampaignAnalysisResponse created successfully

📤 Preparing JSON response...
   Response keys: ['campaign_objective_object', 'segment_preview', 'trigger_suggestions', 'explainability']
   Segment preview size in response: 1234
   AI filters in response: 4
```

### Step 3: Check for Specific Errors

#### Error 1: "Failed to extract AI filters"

If you see:
```
⚠️  Warning: Failed to extract AI filters: ...
```

**Cause:** The AIFilter model is not importing correctly.

**Fix:**
```bash
# Check that backend/api/schemas.py has the AIFilter class
grep -n "class AIFilter" backend/api/schemas.py

# Restart the backend
python run.py
```

#### Error 2: "Error creating SegmentMetadata"

If you see:
```
❌ Error creating SegmentMetadata: ...
   Falling back to metadata without ai_filters
```

**Cause:** The SegmentMetadata Pydantic model doesn't accept the `ai_filters` field.

**Fix:** Verify `backend/api/schemas.py` has:
```python
class SegmentMetadata(BaseModel):
    segment_id: str
    estimated_size: int
    predicted_uplift: float
    predicted_roi: str
    avg_clv_score: float
    avg_cart_value: Optional[float] = None
    common_product_categories: List[str] = []
    demographic_breakdown: Dict[str, Any] = {}
    ai_filters: List[AIFilter] = []  # This line must be present
```

#### Error 3: "Customer DataFrame shape: (0, X)"

If you see 0 rows in the DataFrame:
```
📊 Calculating segment metadata...
   Customer DataFrame shape: (0, 15)
```

**Cause:** The BigQuery query is returning no results.

**Fix:**
1. Check if data exists in BigQuery:
   ```bash
   python scripts/generate_data.py  # Re-run data generation if needed
   ```

2. Check the query being generated:
   - Look for the "Query Preview" in logs
   - Copy the full query and run it directly in BigQuery console
   - Verify the WHERE conditions are correct

3. Common query issues:
   - Time constraint too restrictive (e.g., "48 hours" with old data)
   - CLV threshold too high (no customers above 0.75)
   - Abandoned cart status check failing

### Step 4: Check Frontend Console

Open browser DevTools (F12) and check the Console tab:

```javascript
// When analysis completes, you should see:
Analysis result: {
  campaign_objective_object: {...},
  segment_preview: {
    estimated_size: 1234,  // NOT 0
    ai_filters: [...]       // Array of filters
  },
  trigger_suggestions: [...],
  explainability: {...}
}
```

**If estimated_size is 0 here:**
- The backend is returning 0
- Check backend logs (Step 2)

**If estimated_size is correct in console but shows 0 in UI:**
- Frontend rendering issue
- Check `app.js` line ~196-203 for `displayAnalysisResults()`

### Step 5: Check Network Tab

In browser DevTools, go to Network tab:

1. Filter by "analyze"
2. Click the `/campaigns/analyze` request
3. Check the Response tab

**Should see:**
```json
{
  "segment_preview": {
    "estimated_size": 1234,
    "avg_clv_score": 0.78,
    "ai_filters": [
      {
        "filter_type": "behavior",
        "description": "Target Behavior: Abandoned Cart",
        "sql_condition": "ac.status = 'abandoned'",
        "can_modify": false
      },
      ...
    ]
  }
}
```

**If Response is empty or error:**
- Backend crashed
- Check backend terminal for errors

## Common Fixes

### Fix 1: Restart Backend with Fresh Import

```bash
# Kill any running backend processes
# Ctrl+C in terminal

# Clear Python cache (Windows)
rd /s /q __pycache__
rd /s /q backend\__pycache__
rd /s /q backend\api\__pycache__
rd /s /q backend\models\__pycache__
rd /s /q backend\services\__pycache__

# Restart
python run.py
```

### Fix 2: Verify Schema Updates

Make sure `backend/api/schemas.py` has all new models:

```python
# At the top, after imports
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Around line 61
class AIFilter(BaseModel):
    """Represents a filter applied by AI from campaign objective"""
    filter_type: str
    description: str
    sql_condition: str
    can_modify: bool = True

# Around line 69, in SegmentMetadata
class SegmentMetadata(BaseModel):
    ...
    ai_filters: List[AIFilter] = []  # NEW FIELD

# Around line 97
class FilterRefinementRequest(BaseModel):
    campaign_objective_object: CampaignObjectiveObject
    ai_filter_modifications: Dict[str, Any] = {}
    new_filters: Dict[str, Any] = {}

# Around line 104
class FilterPreviewResponse(BaseModel):
    starting_size: int
    final_size: int
    filters_applied: List[Dict[str, Any]]
    final_avg_clv: float
    final_avg_cart_value: Optional[float] = None
    percentage_retained: float
```

### Fix 3: Check Data Exists in BigQuery

```bash
# Generate fresh data
python scripts/generate_data.py

# Verify data was created
# Should see:
# ✓ Created 10000 customers
# ✓ Created XXXXX transactions
# ✓ Created XXXXX behavioral events
# etc.
```

### Fix 4: Simplify AIFilter Extraction for Testing

Temporarily disable AI filters to isolate the issue:

In `backend/services/segment_service.py`, line ~324:

```python
def _extract_ai_filters(self, coo: CampaignObjectiveObject) -> List:
    """Extract AI-applied filters from Campaign Objective Object"""
    # TEMPORARY: Return empty list to test if this is causing issues
    return []
```

Then test again. If segment size now works:
- The issue is in `_extract_ai_filters()` or AIFilter model
- Check imports and Pydantic model definition

If segment size still 0:
- The issue is elsewhere (BigQuery query, data generation, etc.)

## Verification Checklist

- [ ] Backend starts without errors
- [ ] `python test_backend.py` shows `estimated_size` > 0
- [ ] `test_response.json` contains valid data
- [ ] Backend logs show DataFrame has rows
- [ ] Backend logs show SegmentMetadata created successfully
- [ ] Browser console shows correct `estimated_size`
- [ ] Browser Network tab shows successful API response
- [ ] Frontend displays segment size correctly

## Still Not Working?

If segment size is still 0 after all these steps:

1. **Share Backend Logs:** Copy the full terminal output from backend
2. **Share test_response.json:** Show the actual API response
3. **Share Browser Console:** Show any JavaScript errors
4. **Share BigQuery Status:** 
   ```bash
   # Run and share output
   python -c "from backend.services.bigquery_service import BigQueryService; bq = BigQueryService(); result = bq.query('SELECT COUNT(*) as count FROM aethersegment_cdp.customers'); print(result)"
   ```

## Expected Working Output

When everything is working, your test should show:

```
🚀 AetherSegment AI Backend Test
============================================================
Testing Health Endpoint
============================================================
📊 Health Check Status: 200
✅ Backend is healthy!
   Service: AetherSegment AI

============================================================
Testing Campaign Analysis Endpoint
============================================================
📝 Campaign Objective:
   Increase conversion for abandoned carts...

🔄 Sending POST request to http://localhost:5000/api/v1/campaigns/analyze...
📊 Response Status: 200
✅ Response received successfully!

📊 Segment Preview:
   Segment ID: SEG_PERS_DISC_ABC123
   Estimated Size: 1234         ← NOT 0!
   Avg CLV Score: 0.78
   Predicted Uplift: 0.72
   Predicted ROI: 4-6x
   Avg Cart Value: 125.50

🤖 AI Filters (4):              ← Filters present!
   1. behavior: Target Behavior: Abandoned Cart
   2. timing: Time Window: 48 Hours Post Abandonment
   3. value: Customer Value: High CLV (≥ 0.75, top 25%)
   4. cart_value: Cart Value: Above average

💾 Full response saved to test_response.json
```

This is what you want to see! If you see this, the backend is working correctly and the issue is in the frontend rendering.

