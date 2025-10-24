# Campaign Type Support Status

## Currently Supported Campaign Types ✅

### 1. **Abandoned Cart / Conversion** ✅ FULLY SUPPORTED
**Target Behavior:** `abandoned_cart`

**AI Filters Applied:**
- Time constraint (last 7 days)
- Cart status = abandoned
- Cart value > average
- High CLV (if specified)

**Example:**
```
"Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers"
```

**Expected Segment Size:** 1,000-2,000 customers

---

### 2. **Win-Back / Lapsed Customer** ✅ FULLY SUPPORTED
**Target Behavior:** `lapsed_customer`  
**Campaign Goal:** `win_back`

**AI Filters Applied:**
- Churn probability > 0.6 (high risk of leaving)
- Exclusivity seeker flag = true (for win-back specifically)
- High CLV (if specified)

**Example:**
```
"Win back lapsed customers with exclusive offers"
```

**Expected Segment Size:** 3,000-5,000 customers

---

### 3. **High Engagement / Upsell** ✅ FULLY SUPPORTED
**Target Behavior:** `high_engagement` or `active_customer`

**AI Filters Applied:**
- Content engagement score > 0.7
- High CLV (if specified)

**Example:**
```
"Target highly engaged customers for premium product upsell"
```

**Expected Segment Size:** 2,000-3,000 customers

---

## Partially Supported Campaign Types ⚠️

### 4. **High-Value / Loyalty** ⚠️ PARTIAL SUPPORT
**Target Subgroup:** `high_value_shopper`, `high_clv`, `premium_customer`

**Current Support:**
- ✅ CLV filter (≥ 0.75) works as subgroup filter
- ❌ No dedicated target_behavior for loyalty programs
- ❌ No repeat purchase frequency filter

**Example:**
```
"Target high-value customers for loyalty rewards program"
```

**Current Workaround:** Works if you mention "high-value" or "high CLV" in objective

---

## NOT Supported Campaign Types ❌

### 5. **Cross-Sell** ❌ NOT SUPPORTED
**What's Missing:**
- No product affinity scoring
- No "bought X, recommend Y" logic
- No product category filters
- No recent purchase filters

**Example (won't work properly):**
```
"Cross-sell premium accessories to customers who bought laptops in the last 30 days"
```

**Would Return:** All 10,000 customers (no filtering)

---

### 6. **New Customer Acquisition** ❌ NOT SUPPORTED
**What's Missing:**
- No new customer identification
- No acquisition date filters
- No onboarding stage tracking

**Example (won't work properly):**
```
"Target new customers acquired in the last 7 days for welcome email sequence"
```

**Would Return:** All 10,000 customers (no filtering)

---

### 7. **Retention / Repeat Purchase** ❌ NOT SUPPORTED
**What's Missing:**
- No repeat purchase frequency tracking
- No "time since last purchase" filter
- No loyalty tier filters

**Example (won't work properly):**
```
"Encourage repeat purchases from customers who haven't bought in 60 days"
```

**Would Return:** All 10,000 customers (no filtering)

---

### 8. **Reactivation** ❌ NOT SUPPORTED
**What's Missing:**
- No dormant customer identification
- No "last active date" filter
- Different from lapsed_customer (which uses churn probability)

**Example (won't work properly):**
```
"Reactivate dormant customers who haven't visited in 90 days"
```

**Would Return:** All 10,000 customers (no filtering)

---

## Summary Table

| Campaign Type | Support Level | Filters Applied | Segment Size |
|--------------|---------------|-----------------|--------------|
| Abandoned Cart | ✅ Full | Time, cart status, cart value, CLV | 1,000-2,000 |
| Win-Back/Lapsed | ✅ Full | Churn risk, exclusivity, CLV | 3,000-5,000 |
| High Engagement | ✅ Full | Engagement score, CLV | 2,000-3,000 |
| High-Value/Loyalty | ⚠️ Partial | CLV only | 2,500 |
| Cross-Sell | ❌ None | None | 10,000 (all) |
| New Customer | ❌ None | None | 10,000 (all) |
| Retention | ❌ None | None | 10,000 (all) |
| Reactivation | ❌ None | None | 10,000 (all) |

**Current Coverage:** 3 fully supported, 1 partial, 4 unsupported = **~40% coverage**

---

## What Data Exists in BigQuery?

Let me check what's actually in your dataset:

### Available Columns:
- **customers:** customer_id, email, location, clv_score, acquisition_source, creation_date
- **customer_scores:** discount_sensitivity, free_shipping_sensitivity, churn_probability, content_engagement, exclusivity_seeker_flag, social_proof_affinity
- **transactions:** transaction_id, customer_id, order_value, product_categories, timestamp
- **abandoned_carts:** cart_id, customer_id, cart_value, items, timestamp, status
- **behavioral_events:** event_id, customer_id, event_type, product_viewed, timestamp
- **campaign_history:** campaign_id, customer_id, trigger_type, converted, control_group

### Data That Could Enable More Campaign Types:
✅ **transactions.timestamp** → Can calculate "last purchase date" → Retention campaigns  
✅ **transactions.product_categories** → Can identify product buyers → Cross-sell  
✅ **customers.creation_date** → Can identify new customers → Acquisition campaigns  
✅ **behavioral_events** → Can track activity → Reactivation campaigns  

**THE DATA EXISTS! We just need to add the logic to use it!**

---

## Recommendation: Add Support for 4 More Campaign Types

### Priority 1: **Cross-Sell** (High Business Value)
**Add:**
```python
elif coo.target_behavior == "cross_sell":
    # Filter customers who bought from specific category recently
    conditions.append("""
        EXISTS (
            SELECT 1 FROM `{dataset}.transactions` t
            WHERE t.customer_id = c.customer_id
            AND t.timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND LOWER(t.product_categories) LIKE '%laptop%'
        )
    """)
```

### Priority 2: **New Customer Acquisition** (Common Use Case)
**Add:**
```python
elif coo.target_behavior == "new_customer":
    # Filter customers created in last 7 days
    conditions.append("""
        c.creation_date > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """)
```

### Priority 3: **Retention / Repeat Purchase** (High Value)
**Add:**
```python
elif coo.target_behavior == "retention":
    # Customers who haven't purchased in 30-90 days (at risk)
    conditions.append("""
        c.customer_id IN (
            SELECT customer_id FROM `{dataset}.transactions`
            WHERE timestamp BETWEEN 
                TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND
                TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        )
    """)
```

### Priority 4: **Reactivation** (Dormant Customers)
**Add:**
```python
elif coo.target_behavior == "reactivation":
    # Customers with no activity in 90+ days
    conditions.append("""
        c.customer_id NOT IN (
            SELECT customer_id FROM `{dataset}.behavioral_events`
            WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        )
    """)
```

---

## Action Plan to Reach 80%+ Coverage

### Quick Wins (1-2 hours):
1. ✅ Add new_customer support (simple date filter)
2. ✅ Add retention support (last purchase logic)
3. ✅ Add reactivation support (activity filter)

### Medium Effort (2-4 hours):
4. ✅ Add cross_sell support (product category queries)
5. ✅ Add upsell support (order value progression)

### Nice to Have:
6. Add product affinity scoring
7. Add lifecycle stage segmentation
8. Add RFM (Recency, Frequency, Monetary) scoring

---

## Do You Want Me To Add These?

I can implement support for these 4 additional campaign types right now:
1. **Cross-Sell** - Target customers who bought specific products
2. **New Customer** - Recent signups/acquisitions
3. **Retention** - Customers at risk of not returning
4. **Reactivation** - Dormant/inactive customers

This would bring coverage from **40% → 80%+** and handle most common marketing use cases!

**Should I implement these now?** 🚀

