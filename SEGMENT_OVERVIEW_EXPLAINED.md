# What the Segment Overview Should Show

## 🐛 The Bug - Fixed!

**Problem:** Segment overview was always showing ~1000 customers with the same CLV/metrics

**Root Cause:** The `analyze_campaign()` method was using `LIMIT 1000` to get a sample for trigger recommendations, then calculating all metrics from that same 1000-customer sample instead of the full segment.

```python
# BEFORE (WRONG)
initial_query = self.query_builder.build_segment_query(coo, limit=1000)  # Sample
customer_data = self.bigquery_service.query(initial_query)  # 1000 customers
segment_preview = self._calculate_segment_metadata(customer_data, ...)  # Metrics from sample!
```

**The Fix:** Query the FULL segment without a limit, then calculate metrics from all matching customers.

```python
# AFTER (CORRECT)
full_segment_query = self.query_builder.build_segment_query(coo, limit=None)  # No limit
full_customer_data = self.bigquery_service.query(full_segment_query)  # All matches
segment_preview = self._calculate_segment_metadata(full_customer_data, ...)  # Real metrics!
```

---

## 📊 What Segment Overview SHOULD Show

### Campaign Type: Abandoned Cart (High-Value Shoppers, 48 Hours)

**Example Input:**
```
"Increase conversion for abandoned carts by 20% within 48 hours with 
a personalized discount offer for high-value shoppers"
```

### Expected Segment Overview:

```
╔═══════════════════════════════════════════════════════════════╗
║                    SEGMENT OVERVIEW                           ║
╠═══════════════════════════════════════════════════════════════╣
║  Total Customers:           823                               ║
║  Avg CLV Score:             0.84 (84th percentile)            ║
║  Predicted Uplift:          71%                               ║
║  Predicted ROI:             4-6x                              ║
║  Avg Cart Value:            $145.56                           ║
║                                                               ║
║  Top Cities:                                                  ║
║    • New York         245 customers                           ║
║    • Los Angeles      189 customers                           ║
║    • Chicago          127 customers                           ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🎯 How Each Metric is Calculated

### 1. Total Customers

**What it shows:** Number of unique customers matching ALL campaign criteria

**SQL Logic:**
```sql
SELECT COUNT(DISTINCT c.customer_id)
FROM customers c
INNER JOIN customer_scores cs ON c.customer_id = cs.customer_id
INNER JOIN abandoned_carts ac ON c.customer_id = ac.customer_id
WHERE
  TIMESTAMP(ac.timestamp) > TIMESTAMP('2025-10-21T15:00:00')  -- Last 48 hours
  AND ac.status = 'abandoned'
  AND c.clv_score >= 0.75  -- High-value shoppers (top 25%)
  AND ac.cart_value > (SELECT AVG(cart_value) FROM abandoned_carts)  -- Above avg
```

**Expected Range:**
- **Abandoned Cart (48 hours):** 500-2,000 customers (depending on traffic)
- **Win-back (lapsed >30 days):** 2,000-5,000 customers
- **General high-value:** 2,000-3,000 customers (top 25% of 10,000)

**What to Check:**
- Should be **< total database size** (10,000 in your case)
- Should vary based on campaign criteria
- Tighter criteria (48 hours + high-value + above-avg cart) = smaller segment
- Broader criteria (all lapsed customers) = larger segment

---

### 2. Average CLV Score

**What it shows:** The mean Customer Lifetime Value score for customers in this segment

**Calculation:**
```python
avg_clv = customer_df['clv_score'].mean()
# From BigQuery: average of c.clv_score for all customers in WHERE clause
```

**Expected Values by Campaign Type:**

| Campaign Type | Expected Avg CLV | Reason |
|--------------|------------------|--------|
| **High-Value Segment** | 0.80-0.95 | Filtered for CLV ≥ 0.75 |
| **General Segment** | 0.45-0.55 | Cross-section of all customers |
| **Low-Value Win-back** | 0.20-0.40 | Targeting churned low-value |
| **VIP/Exclusivity** | 0.85-0.99 | Top tier customers only |

**For your abandoned cart campaign:**
- Filtering: `clv_score >= 0.75` (high-value shoppers)
- Expected: **0.80-0.88** (average of customers all above 0.75)
- If showing 0.60 → **Bug!** Should be higher since min is 0.75

**What to Check:**
- Should be ≥ 0.75 for "high-value" campaigns (since that's the filter)
- Should vary based on segment definition
- Should NOT be the same across different campaign types

---

### 3. Predicted Uplift

**What it shows:** Average predicted conversion rate with the recommended trigger

**Calculation:**
```python
# For each customer, calculate uplift score with the recommended trigger
uplift_scores = []
for customer in segment:
    score = calculate_customer_uplift(customer, recommended_trigger)
    uplift_scores.append(score)

predicted_uplift = mean(uplift_scores)
```

**Expected Values:**

| Trigger Type | Segment Quality | Expected Uplift |
|-------------|----------------|-----------------|
| **Discount (High Sensitivity)** | Price-sensitive shoppers | 70-85% |
| **Discount (Low Sensitivity)** | Non-discount seekers | 45-60% |
| **Free Shipping** | Shipping-sensitive | 65-75% |
| **Exclusivity** | VIP/status seekers | 60-75% |
| **Social Proof** | Mixed segment | 50-65% |

**For your high-value abandoned cart:**
- Segment: High CLV, abandoned carts, discount-sensitive
- Trigger: Personalized discount
- Expected: **65-75%**
- If showing 50% → Trigger might not match segment well
- If showing 80%+ → Very strong match!

**What to Check:**
- Should vary based on segment + trigger combination
- High-value + aligned trigger = higher uplift
- Mismatched trigger = lower uplift
- Should NOT always be the same value

---

### 4. Predicted ROI

**What it shows:** Expected return on investment multiplier

**Calculation:**
```python
predicted_roi = "4-6x" if predicted_uplift > 0.6 else "2-4x"
```

**Current Logic:** Simple threshold

**What it SHOULD show (future improvement):**
```python
# More accurate calculation:
campaign_cost = segment_size * email_cost + discount_budget
expected_conversions = segment_size * predicted_uplift
revenue_per_conversion = avg_cart_value * profit_margin
total_revenue = expected_conversions * revenue_per_conversion
roi = (total_revenue - campaign_cost) / campaign_cost

# Example:
# 823 customers × $2/email + $5,000 discount budget = $6,646 cost
# 823 × 71% uplift = 584 conversions
# 584 × $145.56 avg cart × 30% margin = $25,490 revenue
# ROI = ($25,490 - $6,646) / $6,646 = 2.83x → "2-4x" ✓
```

**Expected Values:**
- **High-value segments with aligned triggers:** 4-6x or better
- **General segments:** 2-4x
- **Exploratory campaigns:** 1-2x

**What to Check:**
- Should change based on predicted uplift
- >60% uplift = "4-6x"
- ≤60% uplift = "2-4x"

---

### 5. Average Cart Value (Abandoned Cart Campaigns)

**What it shows:** Mean value of abandoned carts in this segment

**Calculation:**
```python
avg_cart_value = customer_df['cart_value'].mean()
# From abandoned_carts.cart_value for matching customers
```

**Expected Values:**

| Segment Filter | Expected Avg Cart Value |
|---------------|------------------------|
| **Above-average carts only** | $120-$180 |
| **All abandoned carts** | $80-$120 |
| **High-value customer carts** | $150-$250 |
| **Low-value customer carts** | $40-$80 |

**For your campaign:**
- Filter: Above-average cart value + high-value customers
- Expected: **$130-$180**
- If showing $60 → Not filtering correctly
- If showing $200+ → Very high-value segment (good targeting!)

**What to Check:**
- Should be higher than overall average (~$100) since filtered for above-avg
- Should vary by customer value tier
- Multiply by uplift for revenue estimate: 823 × 71% × $145 = ~$84,000 potential

---

### 6. Top Cities (Demographic Breakdown)

**What it shows:** Geographic distribution - top 5 cities by customer count

**Calculation:**
```python
top_cities = customer_df['location_city'].value_counts().head(5).to_dict()
{
  "New York": 245,
  "Los Angeles": 189,
  "Chicago": 127,
  "Houston": 98,
  "Phoenix": 76
}
```

**Expected Pattern:**
- Should reflect population distribution in your customer base
- Top 5 cities should sum to 40-60% of total segment
- Should vary slightly between campaigns (different cities have different behaviors)

**What to Check:**
- Sum of top 5 should be < total segment size
- Distribution should look realistic (not all in one city)
- Should change between different campaign types

---

## 🔍 Real-World Examples

### Example 1: Abandoned Cart - High-Value Shoppers (48 Hours)

**Input:**
```
"Recover abandoned carts from high-value shoppers within 48 hours with personalized discounts"
```

**Query Filters:**
- `ac.timestamp > NOW() - INTERVAL '48 hours'`
- `ac.status = 'abandoned'`
- `c.clv_score >= 0.75`
- `ac.cart_value > AVG(cart_value)`

**Expected Output:**
```
Total Customers:    823
Avg CLV Score:      0.84  (high - filtered for ≥0.75)
Predicted Uplift:   71%   (good match: discount + price-sensitive)
Predicted ROI:      4-6x  (71% > 60% threshold)
Avg Cart Value:     $145.56 (above database average of ~$100)
Top Cities:         NY (245), LA (189), Chicago (127)
```

**Business Meaning:**
- 823 valuable customers left items in cart recently
- They're in top 16% by value (CLV 0.84)
- 71% likely to convert with personalized discount
- Average recovery: $145.56 per converted cart
- Potential revenue: 823 × 71% × $145.56 = $85,067

---

### Example 2: Win-back Lapsed Customers (30+ Days Inactive)

**Input:**
```
"Re-engage customers who haven't purchased in 30+ days with exclusive early access"
```

**Query Filters:**
- `last_purchase_date < NOW() - INTERVAL '30 days'`
- `churn_probability_score > 0.6`

**Expected Output:**
```
Total Customers:    3,247  (larger - many lapsed)
Avg CLV Score:      0.52   (mixed - not filtered by value)
Predicted Uplift:   58%    (moderate - harder to convert lapsed)
Predicted ROI:      2-4x   (58% < 60% threshold)
Avg Cart Value:     N/A    (no carts for lapsed customers)
Top Cities:         NY (892), LA (634), Chicago (421)
```

**Business Meaning:**
- 3,247 customers at risk of churning
- Mixed value (CLV 0.52 = middle tier)
- 58% reactivation rate with exclusivity trigger
- Harder than abandoned cart (lower uplift)
- Larger segment = more scale, lower individual value

---

### Example 3: VIP Upsell Campaign

**Input:**
```
"Upsell premium products to top 10% customers with exclusive VIP access"
```

**Query Filters:**
- `c.clv_score >= 0.90` (top 10%)
- `cs.exclusivity_seeker_flag = TRUE`

**Expected Output:**
```
Total Customers:    412   (small - very selective)
Avg CLV Score:      0.94  (very high - top tier only)
Predicted Uplift:   76%   (excellent - perfect trigger match)
Predicted ROI:      4-6x  (76% > 60%)
Avg Purchase:       $280  (premium customers)
Top Cities:         NY (124), SF (98), LA (71)
```

**Business Meaning:**
- 412 most valuable customers
- Top 6% by lifetime value
- 76% likely to buy with VIP offer
- High AOV ($280 vs $100 average)
- Small but mighty segment

---

## ✅ After the Fix - What You Should See

**Run your backend:**
```powershell
python run.py
```

**Submit a campaign, check terminal:**
```
📊 Fetching full segment data...
🔍 Query Preview:
   SELECT c.customer_id, c.email_address, c.first_name, c.location_city...

✅ Query executed successfully!
   Total customers in segment: 823  ← SHOULD VARY!
   Avg CLV: 0.842  ← SHOULD BE HIGH for high-value campaigns
   Avg Cart Value: $145.56  ← SHOULD BE REALISTIC
```

**Then in the UI:**
- Total Customers: **NOT always 1000** ✅
- Avg CLV: **NOT always 60%** ✅
- Values should **vary by campaign type** ✅
- Numbers should **make business sense** ✅

---

## 🚨 Red Flags (Indicates Bugs)

| Metric | Red Flag | What It Means |
|--------|----------|---------------|
| **Total Customers** | Always ~1000 | Still using sample, not full segment |
| **Total Customers** | >10,000 | Duplicate bug returned |
| **Avg CLV** | Always same (e.g., 0.60) | Not calculating from real data |
| **Avg CLV** | 0.55 for "high-value" filter | Filter not working (should be >0.75) |
| **Predicted Uplift** | Always 50% | Using fallback, calculations failing |
| **Cart Value** | Same across all campaigns | Not filtering correctly |
| **Top Cities** | Sum > Total Customers | Duplicates still present |

---

## 🎯 Summary

**The segment overview should:**
1. ✅ Show the **actual count** of customers matching campaign criteria (NOT always 1000)
2. ✅ Calculate **true averages** from the full segment (NOT from a sample)
3. ✅ **Vary significantly** between different campaign types
4. ✅ Reflect the **quality and characteristics** of the targeted segment
5. ✅ Provide **actionable business insights** for campaign planning

**If you're seeing fixed values, it means:**
- ❌ Querying with LIMIT (we just fixed this!)
- ❌ Using hardcoded defaults instead of real calculations
- ❌ WHERE clauses not working correctly
- ❌ Data not being pulled from BigQuery properly

**Test with the fix and share your results!** You should now see realistic, varying metrics! 🚀

