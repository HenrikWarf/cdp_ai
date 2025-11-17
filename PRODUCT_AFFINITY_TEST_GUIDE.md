# 🏠 Product Affinity Intelligence - Testing Guide

## 📦 What Was Built

A complete product affinity system with **3 levels** of intelligence:

### Level 1: Category Affinity Scores (10 categories)
- `living_room_affinity` - Sofas, sectionals, armchairs
- `bedroom_affinity` - Beds, dressers, nightstands
- `kitchen_dining_affinity` - Tables, chairs, bar stools
- `office_affinity` - Desks, office chairs, workstations
- `outdoor_affinity` - Patio furniture, outdoor seating
- `lighting_affinity` - Floor lamps, table lamps, chandeliers
- `storage_affinity` - Shelving units, cabinets, organizers
- `textiles_affinity` - Rugs, curtains, cushions
- `bathroom_affinity` - Vanities, storage, mirrors
- `decoration_affinity` - Wall art, plants, accessories

**Calculation:** 
- Purchase frequency (60%) + Spending ratio (40%)
- Normalized to 0-1 scale
- Updated with each transaction

### Level 2: Purchase Profile
- `favorite_category` - Most purchased category
- `secondary_category` - 2nd most purchased category
- `cross_category_shopper` - Purchased from 3+ categories (Boolean)
- `price_tier_preference` - Budget (<$300), Mid ($300-800), Premium (>$800)

### Level 3: Product Associations (20 rules)
Cross-sell recommendations with association strength:

**Strong Associations (0.75-0.85):**
- Bedroom → Textiles (0.85)
- Office → Storage (0.82)
- Office → Lighting (0.78)
- Living Room → Lighting (0.75)

**Medium Associations (0.60-0.70):**
- Kitchen → Storage (0.70)
- Bedroom → Lighting (0.65)
- Kitchen → Lighting (0.62)

**Room Progression (0.35-0.45):**
- Living Room → Bedroom (0.42)
- Bedroom → Living Room (0.45)
- Living Room → Kitchen (0.38)

---

## 🚀 Quick Start

### Step 1: Regenerate Data with Product Affinities

```bash
# Activate your Python environment
python scripts/generate_data.py
```

**Expected Output:**
```
Creating BigQuery dataset and tables...
✓ Dataset aether_segment_ai ready
✓ Table customers ready
✓ Table customer_scores ready
✓ Table transactions ready
✓ Table product_associations ready  # <-- NEW TABLE
✓ Table abandoned_carts ready
✓ Table behavioral_events ready
✓ Table campaign_history ready

Generating data...
✓ Generated 10,000 customers
✓ Generated base scores for 10,000 customers

📊 Calculating product affinities from transactions...  # <-- NEW STEP
✓ Enriched 10,000 customer scores with product affinities

🔗 Generating product associations...  # <-- NEW STEP
✓ Generated 20 product association rules

✓ Generated 50,000 transactions
✓ Generated 2,500 abandoned carts
✓ Generated 100,000 behavioral events
✓ Generated 25,000 campaign history records

Loading data into BigQuery...
✓ Loaded 10,000 rows into customers
✓ Loaded 10,000 rows into customer_scores
✓ Loaded 50,000 rows into transactions
✓ Loaded 20 rows into product_associations  # <-- NEW
✓ Loaded 2,500 rows into abandoned_carts
✓ Loaded 100,000 rows into behavioral_events
✓ Loaded 25,000 rows into campaign_history
```

### Step 2: Restart Your Flask Backend

```bash
# In your backend terminal
# Press Ctrl+C to stop
python backend/app.py
```

### Step 3: Test in the UI

---

## 🧪 Test Scenarios

### Test 1: Pre-Defined Product Campaign Template

1. Go to **Campaign Segmentation** page
2. Click **"Pre-defined Templates"** toggle
3. Scroll down to **"Product & Category Campaigns"** accordion
4. Select **"Living Room Cross-Sell"** campaign
5. Click **"Use This Template"**
6. Click **"Analyze Campaign"**

**Expected Result:**
```
Campaign Objective:
Target customers with high living room affinity who purchased sofas 
in the last 60 days to recommend complementary items (coffee tables, 
side tables, lamps) with 15% bundle discount to increase AOV by 30%

Console Output:
   🏠 Product affinity filter: living_room_affinity >= 0.3

Segment Size: ~800-1,200 customers
Customer Cards Show:
  🏠 Living Room (favorite category tag)
  📦 Secondary category (if any)
  💎/⭐/💰 Price tier badge
```

---

### Test 2: Custom Product Campaign (Free Text)

Use the free text input with this campaign:

```
Target premium bedroom furniture buyers to complete their bedroom 
setup with matching nightstands and luxury bedding
```

**Expected Result:**
```
Console Output:
   🏠 Product affinity filter: bedroom_affinity >= 0.3
   💎 Premium tier filter applied

Segment Size: ~300-500 customers
Customer Cards Show:
  🏠 Bedroom (favorite category)
  💎 premium (price tier)
```

---

### Test 3: Cross-Category Campaign

Campaign text:
```
Target cross-category shoppers with loyalty rewards to increase 
repeat purchases across multiple furniture categories
```

**Expected Result:**
```
Console Output:
   🔀 Cross-category shopper filter applied

Segment Size: ~2,500-3,500 customers
Customer Cards Show:
  🏠 Multiple category tags
  🔀 Indicators of diverse purchases
```

---

### Test 4: Office Furniture Campaign

Campaign text:
```
Target customers with office furniture affinity to upgrade their 
home office with ergonomic chairs and storage solutions
```

**Expected Result:**
```
Console Output:
   🏠 Product affinity filter: office_affinity >= 0.3

Segment Size: ~900-1,300 customers
Customer Cards Show:
  🏠 Office (favorite category)
```

---

### Test 5: Budget-Tier Campaign

Campaign text:
```
Target budget-conscious customers with affordable storage solutions 
and organization furniture
```

**Expected Result:**
```
Console Output:
   🏠 Product affinity filter: storage_affinity >= 0.3
   💰 Budget tier filter applied

Segment Size: ~400-700 customers
Customer Cards Show:
  🏠 Storage & Organization
  💰 budget (price tier)
```

---

## 🔍 Verification Checklist

### Backend Verification

✅ **BigQuery Tables Created:**
```sql
SELECT * FROM `aether_segment_ai.product_associations` LIMIT 10
SELECT favorite_category, COUNT(*) as count 
FROM `aether_segment_ai.customer_scores` 
WHERE favorite_category IS NOT NULL
GROUP BY favorite_category
```

✅ **Customer Scores Include Affinity Fields:**
```sql
SELECT 
  customer_id,
  living_room_affinity,
  bedroom_affinity,
  favorite_category,
  price_tier_preference
FROM `aether_segment_ai.customer_scores`
WHERE living_room_affinity > 0.5
LIMIT 10
```

### Frontend Verification

✅ **Campaign Templates:**
- 5 new product-specific campaigns in "Product & Category Campaigns" group
- All templates auto-populate text input when selected

✅ **Customer Cards Display:**
- Product category tags (🏠 emoji)
- Secondary category tags (📦 emoji)
- Price tier badges (💎/⭐/💰)
- Proper styling with gradient backgrounds

✅ **Console Logs:**
- Product affinity filter messages in console
- Query builder output showing SQL filters applied

---

## 📊 Expected Data Distribution

After data generation, you should see approximately:

- **10,000 customers** with product affinity scores
- **~70-80%** have a favorite_category (7,000-8,000 customers)
- **~50-60%** have cross_category_shopper = true (5,000-6,000 customers)
- **Price Tier Distribution:**
  - Budget: ~35% (3,500 customers)
  - Mid: ~40% (4,000 customers)
  - Premium: ~25% (2,500 customers)

- **Top Categories by Affinity:**
  - Living Room: ~20% of customers
  - Bedroom: ~18% of customers
  - Kitchen & Dining: ~15% of customers
  - Office: ~12% of customers
  - Other categories: ~35% combined

---

## 🐛 Troubleshooting

### Issue: "column not found: favorite_category"

**Solution:** The customer_scores table needs to be recreated
```bash
# Drop and recreate the table
python scripts/generate_data.py
```

### Issue: Product filters not applying

**Solution:** Check console for filter messages
```javascript
// You should see in browser console:
🏠 Product affinity filter: living_room_affinity >= 0.3
```

If not appearing, verify:
1. Campaign text includes product keywords (living, bedroom, office, etc.)
2. Backend query_builder.py has _extract_product_affinity_filters method
3. Flask backend was restarted after code changes

### Issue: Customer cards don't show product tags

**Solution:** Check that:
1. Backend SELECT clause includes: `cs.favorite_category, cs.secondary_category, cs.price_tier_preference`
2. Customer profiles in API response include these fields
3. CSS is loaded: `frontend/css/dashboard.css` has `.affinity-tag` styles

---

## 🎯 Success Criteria

Your implementation is working correctly if:

1. ✅ Data generation completes with product affinity calculations
2. ✅ Product association table is created with 20 rules
3. ✅ Customer cards display category and tier tags
4. ✅ Product-specific campaigns filter by affinity
5. ✅ Console shows "Product affinity filter" messages
6. ✅ Segment sizes are reasonable (500-3,000 customers per campaign)
7. ✅ Different campaigns yield different segments based on product preferences

---

## 🚀 Next Steps

Once testing is complete, you can:

1. **Query Product Associations:**
   ```sql
   SELECT * FROM `aether_segment_ai.product_associations`
   WHERE primary_category = 'Living Room'
   ORDER BY association_strength DESC
   ```

2. **Analyze Customer Segments by Product:**
   ```sql
   SELECT 
     favorite_category,
     price_tier_preference,
     COUNT(*) as customer_count,
     AVG(clv_score) as avg_clv
   FROM `aether_segment_ai.customer_scores`
   WHERE favorite_category IS NOT NULL
   GROUP BY favorite_category, price_tier_preference
   ORDER BY customer_count DESC
   ```

3. **Build Advanced Product Campaigns:**
   - Multi-product bundle campaigns
   - Seasonal product launches
   - Category-specific win-back campaigns
   - Cross-sell based on association rules

---

## 📚 Technical Details

### Files Modified

**Backend:**
- `scripts/generate_data.py` - Added affinity calculation logic
- `backend/models/query_builder.py` - Added product affinity filtering
- `backend/api/schemas.py` - Added product fields to CustomerProfile
- `backend/services/segment_service.py` - Updated profile generation

**Frontend:**
- `frontend/js/data/campaignTemplates.js` - Added 5 product campaigns
- `frontend/js/app.js` - Added product tag rendering
- `frontend/css/dashboard.css` - Added affinity tag styles

**Documentation:**
- `README.md` - Added Product Affinity Intelligence section
- `PRODUCT_AFFINITY_TEST_GUIDE.md` - This file

### New Database Schema

```sql
-- customer_scores table additions
ALTER TABLE customer_scores ADD COLUMN living_room_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN bedroom_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN kitchen_dining_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN office_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN outdoor_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN lighting_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN storage_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN textiles_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN bathroom_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN decoration_affinity FLOAT64;
ALTER TABLE customer_scores ADD COLUMN favorite_category STRING;
ALTER TABLE customer_scores ADD COLUMN secondary_category STRING;
ALTER TABLE customer_scores ADD COLUMN cross_category_shopper BOOL;
ALTER TABLE customer_scores ADD COLUMN price_tier_preference STRING;

-- product_associations table (new)
CREATE TABLE product_associations (
  primary_category STRING NOT NULL,
  associated_category STRING NOT NULL,
  association_strength FLOAT64,
  common_sequence INT64
);
```

---

**Questions?** Check the console logs, BigQuery tables, and API responses for debugging information!






