# Testing Guide - Three-Section Refinement UI

## Quick Start

### 1. Start the Backend
```bash
python run.py
```

Expected output:
```
✓ Configuration validated
============================================================
  AetherSegment AI - Backend Server
============================================================
  Running on: http://localhost:5000
  Debug mode: True
  Environment: development
  GCP Project: ml-developer-project-fe07
  BigQuery Dataset: aethersegment_cdp
============================================================
```

### 2. Open the Frontend
Open `frontend/index.html` in your browser or use a local server:
```bash
# If you have Python
cd frontend
python -m http.server 8000
# Then open http://localhost:8000
```

## Test Scenarios

### Scenario 1: Full Workflow with Refinement

**Step 1: Enter Campaign Objective**
```
Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers
```

**Expected Result:**
- Campaign input accepted
- Analysis begins (loading state)

**Step 2: Review AI Analysis**
- ✅ See AI Campaign Interpretation (COO display)
- ✅ See Full Eligible Segment metrics:
  - Total Customers (should match actual data, not inflated)
  - Avg CLV Score (calculated from full segment)
  - Predicted Uplift (from top trigger)
  - Predicted ROI
  - Avg Cart Value (for abandoned cart campaign)
- ✅ See AI-Applied Filters:
  - "behavior: Target Behavior: Abandoned Cart"
  - "timing: Time Window: 48 Hours Post Abandonment"
  - "value: Customer Value: High CLV (≥ 0.75, top 25%)"
  - "cart_value: Cart Value: Above average"

**Step 3: Refine Segment (Optional)**

Click "Proceed to Refine Segment"

**Section 1: AI-Applied Filters**
- ✅ See same AI filters displayed with gradient badges

**Section 2: Add Additional Filters**
1. Select Country: "United States"
2. Enter Minimum CLV Score: 80
3. Click "Preview Filter Impact"

**Expected Result:**
- Loading state on button
- Section 3 appears with preview

**Section 3: Filter Impact Preview**
- ✅ See before/after comparison:
  - Starting Size (e.g., 5,000 customers)
  - Final Size (e.g., 2,300 customers)
  - Percentage retained (e.g., 46%)
- ✅ See filters applied list:
  - "Country: United States → 3,500 customers"
  - "CLV Score ≥ 80% → 2,300 customers"
- ✅ "Apply Filters & Continue" button appears

**Step 4: Select Trigger & Activate**

Click "Apply Filters & Continue" or "Skip to Trigger Selection"

- ✅ See Final Segment Overview (with or without manual filters)
- ✅ See Recommended Triggers (ranked by AI)
- ✅ See Explainability section
- ✅ Can create segment

### Scenario 2: Skip Refinement

**Steps:**
1. Enter campaign objective
2. In Step 2, click "Skip to Trigger Selection"
3. Go directly to Step 4

**Expected Result:**
- Skip Step 3 entirely
- Use full AI-filtered segment
- See triggers and create segment

### Scenario 3: Navigate Back and Forth

**Steps:**
1. Complete analysis (Step 2)
2. Click "Proceed to Refine Segment"
3. Click "← Back to Analysis"
4. Should return to Step 2
5. Click "Proceed to Refine Segment" again
6. Add filters and preview
7. Click "Apply Filters & Continue"
8. In Step 4, click "← Back to Refine"
9. Should return to Step 3 with filters preserved

**Expected Result:**
- Smooth navigation between steps
- State is preserved
- No data loss

### Scenario 4: Clear Filters

**Steps:**
1. In Step 3, add filters (country, CLV, etc.)
2. Click "Preview Filter Impact"
3. See preview results
4. Click "Clear All Filters"

**Expected Result:**
- All filter inputs reset to empty/default
- Preview section hidden
- "Apply Filters & Continue" button hidden

### Scenario 5: Start New Campaign

**Steps:**
1. Complete full workflow
2. Create a segment
3. Click "Create Another Campaign" or "Start New Campaign"

**Expected Result:**
- All state cleared
- Return to Step 1 (campaign input)
- All filters cleared
- Ready for new campaign

## Backend API Testing

### Test Filter Preview Endpoint

```bash
curl -X POST http://localhost:5000/api/v1/segments/preview-filters \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_objective_object": {
      "campaign_goal": "conversion",
      "target_behavior": "abandoned_cart",
      "target_subgroup": "high_value_shopper",
      "metric_target": {
        "type": "conversion_rate_increase",
        "value": 0.2
      },
      "time_constraint": "48_hours_post_abandonment",
      "proposed_intervention": "personalized_discount_offer",
      "underlying_assumptions": ["price_sensitive", "urgency_responsive"]
    },
    "new_filters": {
      "location_country": "United States",
      "clv_min": 0.8
    }
  }'
```

**Expected Response:**
```json
{
  "starting_size": 5000,
  "final_size": 2300,
  "percentage_retained": 46.0,
  "filters_applied": [
    {
      "type": "location",
      "description": "Country: United States",
      "impact": 3500
    },
    {
      "type": "value",
      "description": "CLV Score ≥ 80%",
      "impact": 2300
    }
  ],
  "final_avg_clv": 0.856,
  "final_avg_cart_value": 125.50
}
```

### Test Campaign Analysis (Should Return AI Filters)

```bash
curl -X POST http://localhost:5000/api/v1/campaigns/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers"
  }'
```

**Expected Response:**
Should include in `segment_preview`:
```json
{
  "segment_preview": {
    "segment_id": "...",
    "estimated_size": 5000,
    "ai_filters": [
      {
        "filter_type": "behavior",
        "description": "Target Behavior: Abandoned Cart",
        "sql_condition": "ac.status = 'abandoned'",
        "can_modify": false
      },
      {
        "filter_type": "timing",
        "description": "Time Window: 48 Hours Post Abandonment",
        "sql_condition": "TIMESTAMP(ac.timestamp) > TIMESTAMP(...)",
        "can_modify": true
      },
      {
        "filter_type": "value",
        "description": "Customer Value: High CLV (≥ 0.75, top 25%)",
        "sql_condition": "c.clv_score >= 0.75",
        "can_modify": true
      },
      {
        "filter_type": "cart_value",
        "description": "Cart Value: Above average",
        "sql_condition": "ac.cart_value > (SELECT AVG(cart_value) FROM abandoned_carts)",
        "can_modify": true
      }
    ],
    ...
  }
}
```

## Troubleshooting

### Issue: AI Filters Not Showing
**Check:**
- Backend logs for errors in `_extract_ai_filters()`
- Browser console for JavaScript errors
- Verify `ai_filters` field in API response

**Fix:**
- Ensure `backend/services/segment_service.py` has `_extract_ai_filters()` method
- Check that `SegmentMetadata` includes `ai_filters` field

### Issue: Filter Preview Not Working
**Check:**
- Network tab in browser DevTools
- Backend logs for errors in `preview_filter_impact()`
- Verify filter values are being collected correctly

**Fix:**
- Check that `apiClient.previewFilters()` is called with correct parameters
- Verify backend has `location_country` column in query results
- Check that filters are being applied to DataFrame correctly

### Issue: Navigation Not Working
**Check:**
- Browser console for JavaScript errors
- Verify all button IDs match event listeners
- Check that sections are being shown/hidden correctly

**Fix:**
- Ensure all new section IDs are in HTML
- Verify navigation methods are called correctly
- Check that section references are initialized in constructor

### Issue: Segment Numbers Still Incorrect
**Check:**
- Backend logs showing query execution
- Verify `query_builder.build_segment_query(coo, limit=None)`
- Check that there are no duplicate rows in results

**Fix:**
- Ensure no `LIMIT` in initial segment query
- Verify no `LEFT JOIN` causing duplicates
- Check that aggregations are calculated correctly

## Success Criteria

✅ **Step 2: Analysis Results**
- AI filters are displayed clearly
- Segment metrics are accurate (not inflated)
- Cart value filter input is shown for abandoned cart campaigns
- All navigation buttons work

✅ **Step 3: Refine Segment**
- AI filters section shows applied filters
- Manual filter inputs accept values
- Preview button triggers API call
- Preview shows before/after comparison
- Apply button appears after preview

✅ **Step 4: Trigger Selection**
- Final segment shows correct metrics
- Triggers are displayed and ranked
- Create segment works

✅ **Navigation**
- Can move forward through steps
- Can go back to previous steps
- Can skip refinement
- Can start new campaign

✅ **Backend**
- Filter preview endpoint works
- AI filters are extracted and returned
- Metrics are calculated from full segment
- No duplicate rows

## Console Debugging

Open browser DevTools (F12) and look for:

```javascript
// When analysis completes
console.log('Analysis result:', analysis);
// Should show: ai_filters array in segment_preview

// When previewing filters
console.log('Preview result:', preview);
// Should show: starting_size, final_size, filters_applied

// When navigating
console.log('Showing section:', sectionName);
// Should confirm which section is displayed
```

## Browser Network Tab

Check these API calls:
1. `POST /api/v1/campaigns/analyze` - Returns analysis with ai_filters
2. `POST /api/v1/segments/preview-filters` - Returns filter preview
3. `POST /api/v1/segments/create` - Creates final segment

Verify:
- Status codes are 200
- Response bodies contain expected data
- No CORS errors
- No server errors (500)

Good luck testing! 🚀

