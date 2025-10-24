# Enhanced UI: Step-by-Step Filtering Flow

## 🎯 Updated Flow (5 Steps)

```
1. Campaign Input
   ↓
2. Full Eligible Segment (AI criteria)
   ↓
3. Apply Standard Filters (Optional) ← NEW!
   ↓
4. Refine by Trigger (Optional)
   ↓
5. Final Activation
```

---

## 📊 Available Filters Based on Your Data

### From BigQuery Schema:

**Demographics (from `customers` table):**
- ✅ Location City
- ✅ Location Country
- ✅ Acquisition Source
- ✅ Customer Age (creation_date → tenure)

**Value Metrics (from `customers` + `customer_scores` tables):**
- ✅ CLV Score Range
- ✅ Churn Probability

**Behavioral Scores (from `customer_scores` table):**
- ✅ Discount Sensitivity
- ✅ Free Shipping Sensitivity
- ✅ Exclusivity Seeker (Yes/No)
- ✅ Social Proof Affinity
- ✅ Content Engagement Score

**Transaction Metrics (calculated from `transactions` table):**
- ✅ Average Order Value
- ✅ Purchase Frequency
- ✅ Last Purchase Date

**Campaign-Specific (for abandoned cart campaigns):**
- ✅ Cart Value Range
- ✅ Items in Cart

---

## 🎨 Complete Step-by-Step UI Design

### Step 1: Campaign Input
```
┌─────────────────────────────────────────┐
│  📝 STEP 1: Define Campaign Objective   │
│  ─────────────────────────────────────  │
│  [Text area with example campaign]      │
│  [Analyze Campaign] button              │
└─────────────────────────────────────────┘
```

### Step 2: Full Eligible Segment (AI Criteria Only)
```
┌─────────────────────────────────────────┐
│  ✅ STEP 2: Full Eligible Segment       │
│  ─────────────────────────────────────  │
│  📊 AI identified these criteria:       │
│  • High-value shoppers (CLV ≥ 0.75)    │
│  • Abandoned cart in last 48 hours     │
│  • Cart value above average             │
│                                         │
│  SEGMENT OVERVIEW                       │
│  ┌─────────────────────────────────┐   │
│  │ Total Customers:     2,847      │   │
│  │ Avg CLV Score:       0.84       │   │
│  │ Avg Cart Value:      $145       │   │
│  │ Top Cities:          15 cities  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Next Steps:                            │
│  ┌─────────────────────────────────┐   │
│  │ [✓ Proceed with Full Segment]  │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ [🔍 Apply Standard Filters]     │   │ ← NEW!
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ [🎯 Refine by AI Trigger]       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Step 3: Apply Standard Filters (NEW!)
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 STEP 3: Apply Standard Filters (Optional)                │
│  ──────────────────────────────────────────────────────────  │
│  Refine your segment using traditional criteria. All filters │
│  are optional - only use what makes sense for your campaign. │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  📍 LOCATION FILTERS                                 │    │
│  │  ──────────────────────────────────────────────────  │    │
│  │                                                       │    │
│  │  Filter by City:                                     │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ ☐ All Cities (2,847 customers)              │   │    │
│  │  │ ☑ Selected Cities Only:                     │   │    │
│  │  │                                              │   │    │
│  │  │   Multi-select dropdown:                    │   │    │
│  │  │   ┌────────────────────────────────────┐    │   │    │
│  │  │   │ ☑ New York         (842 customers) │    │   │    │
│  │  │   │ ☑ Los Angeles      (621 customers) │    │   │    │
│  │  │   │ ☐ Chicago          (387 customers) │    │   │    │
│  │  │   │ ☐ Houston          (294 customers) │    │   │    │
│  │  │   │ ☐ Phoenix          (201 customers) │    │   │    │
│  │  │   │ ☐ Philadelphia     (189 customers) │    │   │    │
│  │  │   │ ... (show all 15 cities)           │    │   │    │
│  │  │   └────────────────────────────────────┘    │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                       │    │
│  │  Preview: 1,463 customers match selected cities     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  💰 VALUE FILTERS                                    │    │
│  │  ──────────────────────────────────────────────────  │    │
│  │                                                       │    │
│  │  CLV Score Range:                                    │    │
│  │  ☐ Apply CLV Filter                                 │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ Min: [0.75] ──────●──────── Max: [1.00]     │   │    │
│  │  │      (Currently: AI set minimum at 0.75)    │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                       │    │
│  │  Average Order Value:                                │    │
│  │  ☐ Apply AOV Filter                                 │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ Min: [$___] ───●─────── Max: [$___]         │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                       │    │
│  │  Cart Value (Abandoned Cart campaigns only):        │    │
│  │  ☐ Apply Cart Value Filter                          │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │ Min: [$100] ──●──────── Max: [$500]         │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  🎯 BEHAVIORAL FILTERS                               │    │
│  │  ──────────────────────────────────────────────────  │    │
│  │                                                       │    │
│  │  Discount Sensitivity:                               │    │
│  │  ☐ Only High Discount Sensitivity (>0.7)            │    │
│  │  ☐ Only Medium-Low (<0.5)                           │    │
│  │                                                       │    │
│  │  Customer Type:                                      │    │
│  │  ☐ Exclusivity Seekers Only                         │    │
│  │  ☐ High Social Proof Affinity (>0.7)                │    │
│  │                                                       │    │
│  │  Engagement:                                         │    │
│  │  ☐ High Content Engagement (>0.6)                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ⏰ TIMING FILTERS                                   │    │
│  │  ──────────────────────────────────────────────────  │    │
│  │                                                       │    │
│  │  Customer Tenure:                                    │    │
│  │  ☐ New Customers (< 30 days)                        │    │
│  │  ☐ Established (30-365 days)                        │    │
│  │  ☐ Long-term (> 365 days)                           │    │
│  │                                                       │    │
│  │  Last Purchase:                                      │    │
│  │  ☐ Active (< 30 days)                               │    │
│  │  ☐ At Risk (30-90 days)                             │    │
│  │  ☐ Lapsed (> 90 days)                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  📢 ACQUISITION FILTERS                              │    │
│  │  ──────────────────────────────────────────────────  │    │
│  │                                                       │    │
│  │  Acquisition Source:                                 │    │
│  │  ☐ Organic Search        ☐ Paid Search              │    │
│  │  ☐ Social Media          ☐ Email Campaign           │    │
│  │  ☐ Referral              ☐ Direct                   │    │
│  │  ☐ Display Ads           ☐ Affiliate                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📊 FILTER IMPACT PREVIEW                            │   │
│  │  ───────────────────────────────────────────────────  │   │
│  │                                                        │   │
│  │  Starting Segment:         2,847 customers           │   │
│  │  After Location Filter:    1,463 customers (-48.6%)  │   │
│  │  After CLV Filter:         1,463 customers (no change)│  │
│  │  After Cart Value Filter:  1,158 customers (-20.8%)  │   │
│  │  ─────────────────────────────────────────────────    │   │
│  │  FINAL FILTERED SEGMENT:   1,158 customers           │   │
│  │  Avg CLV:                  0.86 (↑ from 0.84)        │   │
│  │  Avg Cart Value:           $168 (↑ from $145)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────┐              │
│  │  [← Back to Full Segment]                │              │
│  │  [Clear All Filters]                      │              │
│  │  [Apply Filters & Continue →]             │              │
│  └───────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Refine by AI Trigger (Existing)
```
┌─────────────────────────────────────────┐
│  🎯 STEP 4: Refine by Trigger (Optional)│
│  ─────────────────────────────────────  │
│  Starting with: 1,158 customers         │
│                                         │
│  [Trigger cards as before...]           │
│                                         │
│  ○ Personalized Discount                │
│    ~817 customers (70% of filtered)     │
│                                         │
│  ○ Free Shipping                        │
│    ~694 customers (60% of filtered)     │
│                                         │
│  ● No Trigger Filter                    │
│    1,158 customers (keep all)           │
└─────────────────────────────────────────┘
```

### Step 5: Final Activation
```
┌─────────────────────────────────────────┐
│  🚀 STEP 5: Final Segment               │
│  ─────────────────────────────────────  │
│  Applied Filters:                       │
│  ✓ AI Criteria (high-value, 48hr cart) │
│  ✓ Location (NYC, LA only)              │
│  ✓ Cart Value ($100-$500)               │
│  ✓ Trigger (Personalized Discount)      │
│                                         │
│  Final Segment: 817 customers           │
│  [Export] [Activate]                    │
└─────────────────────────────────────────┘
```

---

## 🔧 Implementation Details

### 1. Filter Component Structure

```javascript
// frontend/js/components/standardFilters.js

class StandardFiltersComponent {
  constructor() {
    this.filters = {
      location: {
        enabled: false,
        cities: []
      },
      clv: {
        enabled: false,
        min: 0,
        max: 1
      },
      aov: {
        enabled: false,
        min: null,
        max: null
      },
      cartValue: {
        enabled: false,
        min: null,
        max: null
      },
      discountSensitivity: {
        enabled: false,
        level: null // 'high', 'low'
      },
      exclusivitySeeker: {
        enabled: false,
        value: true
      },
      socialProof: {
        enabled: false,
        min: null
      },
      customerTenure: {
        enabled: false,
        category: null // 'new', 'established', 'longterm'
      },
      lastPurchase: {
        enabled: false,
        category: null // 'active', 'atrisk', 'lapsed'
      },
      acquisitionSource: {
        enabled: false,
        sources: []
      }
    };
    
    this.baseSegment = null;
    this.currentPreview = null;
  }

  async renderFilters(baseSegmentData) {
    this.baseSegment = baseSegmentData;
    
    const container = document.getElementById('standard-filters-container');
    
    // Render each filter group
    container.innerHTML = `
      ${this.renderLocationFilters()}
      ${this.renderValueFilters()}
      ${this.renderBehavioralFilters()}
      ${this.renderTimingFilters()}
      ${this.renderAcquisitionFilters()}
      ${this.renderFilterPreview()}
    `;
    
    this.attachEventListeners();
  }

  renderLocationFilters() {
    // Get unique cities from base segment
    const cities = this.baseSegment.demographic_breakdown?.top_cities || {};
    
    return `
      <div class="filter-group">
        <h3>📍 Location Filters</h3>
        <div class="filter-option">
          <label>
            <input type="checkbox" id="location-filter-enabled">
            Filter by City
          </label>
        </div>
        <div id="city-selector" style="display: none;">
          ${Object.entries(cities).map(([city, count]) => `
            <label class="city-checkbox">
              <input type="checkbox" name="city" value="${city}">
              ${city} (${count} customers)
            </label>
          `).join('')}
        </div>
      </div>
    `;
  }

  renderValueFilters() {
    const currentCLV = this.baseSegment.avg_clv_score || 0.5;
    
    return `
      <div class="filter-group">
        <h3>💰 Value Filters</h3>
        
        <!-- CLV Range -->
        <div class="filter-option">
          <label>
            <input type="checkbox" id="clv-filter-enabled">
            Filter by CLV Score
          </label>
          <div id="clv-range-selector" style="display: none;">
            <div class="range-inputs">
              <label>Min: 
                <input type="number" id="clv-min" min="0" max="1" step="0.01" value="${currentCLV}">
              </label>
              <label>Max: 
                <input type="number" id="clv-max" min="0" max="1" step="0.01" value="1.00">
              </label>
            </div>
            <input type="range" id="clv-slider" min="0" max="100" value="${currentCLV * 100}">
          </div>
        </div>

        <!-- AOV Range -->
        <div class="filter-option">
          <label>
            <input type="checkbox" id="aov-filter-enabled">
            Filter by Average Order Value
          </label>
          <div id="aov-range-selector" style="display: none;">
            <div class="range-inputs">
              <label>Min: $<input type="number" id="aov-min" min="0" step="10"></label>
              <label>Max: $<input type="number" id="aov-max" min="0" step="10"></label>
            </div>
          </div>
        </div>

        <!-- Cart Value (only for abandoned cart campaigns) -->
        ${this.baseSegment.avg_cart_value ? `
          <div class="filter-option">
            <label>
              <input type="checkbox" id="cart-value-filter-enabled">
              Filter by Cart Value
            </label>
            <div id="cart-value-range-selector" style="display: none;">
              <div class="range-inputs">
                <label>Min: $<input type="number" id="cart-min" min="0" step="10" value="0"></label>
                <label>Max: $<input type="number" id="cart-max" min="0" step="10" value="1000"></label>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  renderBehavioralFilters() {
    return `
      <div class="filter-group">
        <h3>🎯 Behavioral Filters</h3>
        
        <div class="filter-option">
          <label>
            <input type="checkbox" id="discount-sensitivity-high">
            High Discount Sensitivity Only (>0.7)
          </label>
        </div>

        <div class="filter-option">
          <label>
            <input type="checkbox" id="exclusivity-seekers">
            Exclusivity Seekers Only
          </label>
        </div>

        <div class="filter-option">
          <label>
            <input type="checkbox" id="social-proof-high">
            High Social Proof Affinity (>0.7)
          </label>
        </div>

        <div class="filter-option">
          <label>
            <input type="checkbox" id="content-engagement-high">
            High Content Engagement (>0.6)
          </label>
        </div>
      </div>
    `;
  }

  renderTimingFilters() {
    return `
      <div class="filter-group">
        <h3>⏰ Timing Filters</h3>
        
        <div class="filter-option">
          <label>Customer Tenure:</label>
          <select id="tenure-filter">
            <option value="">All Customers</option>
            <option value="new">New (< 30 days)</option>
            <option value="established">Established (30-365 days)</option>
            <option value="longterm">Long-term (> 365 days)</option>
          </select>
        </div>

        <div class="filter-option">
          <label>Last Purchase:</label>
          <select id="last-purchase-filter">
            <option value="">Any Time</option>
            <option value="active">Active (< 30 days)</option>
            <option value="atrisk">At Risk (30-90 days)</option>
            <option value="lapsed">Lapsed (> 90 days)</option>
          </select>
        </div>
      </div>
    `;
  }

  renderAcquisitionFilters() {
    const sources = [
      'organic_search', 'paid_search', 'social_media', 'email_campaign',
      'referral', 'direct', 'display_ads', 'affiliate'
    ];
    
    return `
      <div class="filter-group">
        <h3>📢 Acquisition Filters</h3>
        <div class="filter-option">
          <label>
            <input type="checkbox" id="acquisition-filter-enabled">
            Filter by Acquisition Source
          </label>
          <div id="acquisition-selector" style="display: none;">
            ${sources.map(source => `
              <label class="acquisition-checkbox">
                <input type="checkbox" name="acquisition" value="${source}">
                ${this.formatSourceName(source)}
              </label>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  renderFilterPreview() {
    return `
      <div class="filter-preview-box">
        <h3>📊 Filter Impact Preview</h3>
        <div id="filter-impact">
          <div class="impact-row">
            <span>Starting Segment:</span>
            <strong>${this.baseSegment.estimated_size} customers</strong>
          </div>
          <div id="active-filters-impact">
            <!-- Dynamically updated as filters are applied -->
          </div>
          <div class="impact-row final">
            <span>FINAL FILTERED SEGMENT:</span>
            <strong id="final-segment-size">${this.baseSegment.estimated_size} customers</strong>
          </div>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Location filter toggle
    document.getElementById('location-filter-enabled')?.addEventListener('change', (e) => {
      document.getElementById('city-selector').style.display = e.target.checked ? 'block' : 'none';
      this.updateFilters();
    });

    // City checkboxes
    document.querySelectorAll('input[name="city"]').forEach(checkbox => {
      checkbox.addEventListener('change', () => this.updateFilters());
    });

    // CLV filter toggle and inputs
    document.getElementById('clv-filter-enabled')?.addEventListener('change', (e) => {
      document.getElementById('clv-range-selector').style.display = e.target.checked ? 'block' : 'none';
      this.updateFilters();
    });

    // All filter inputs trigger preview update
    document.querySelectorAll('input, select').forEach(element => {
      element.addEventListener('change', () => this.updateFilters());
      if (element.type === 'number' || element.type === 'range') {
        element.addEventListener('input', () => this.debounceUpdateFilters());
      }
    });
  }

  async updateFilters() {
    // Collect current filter state
    this.filters = this.collectFilterState();
    
    // Request preview from backend
    const preview = await this.apiClient.previewStandardFilters(
      this.baseSegment.segment_id,
      this.filters
    );
    
    this.currentPreview = preview;
    this.updatePreviewDisplay(preview);
  }

  collectFilterState() {
    return {
      location: {
        enabled: document.getElementById('location-filter-enabled')?.checked || false,
        cities: Array.from(document.querySelectorAll('input[name="city"]:checked'))
          .map(cb => cb.value)
      },
      clv: {
        enabled: document.getElementById('clv-filter-enabled')?.checked || false,
        min: parseFloat(document.getElementById('clv-min')?.value || 0),
        max: parseFloat(document.getElementById('clv-max')?.value || 1)
      },
      // ... collect all other filters
    };
  }

  updatePreviewDisplay(preview) {
    const impactContainer = document.getElementById('active-filters-impact');
    impactContainer.innerHTML = '';
    
    if (preview.filters_applied && preview.filters_applied.length > 0) {
      preview.filters_applied.forEach(filter => {
        impactContainer.innerHTML += `
          <div class="impact-row">
            <span>After ${filter.name}:</span>
            <strong>${filter.size} customers (${filter.change})</strong>
          </div>
        `;
      });
    }
    
    document.getElementById('final-segment-size').textContent = 
      `${preview.final_size} customers`;
  }

  getAppliedFilters() {
    return this.filters;
  }

  formatSourceName(source) {
    return source.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  }

  debounceUpdateFilters = this.debounce(() => this.updateFilters(), 300);

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}
```

---

## 🔌 Backend API Changes

### New Endpoint: Preview Standard Filters

```python
# backend/api/routes.py

@api.route('/filters/preview', methods=['POST'])
def preview_standard_filters():
    """
    Preview the impact of standard filters on a segment
    
    Request Body:
        {
            "segment_id": "SEG_20251023_...",
            "campaign_objective_object": { ... },
            "filters": {
                "location": {"enabled": true, "cities": ["New York", "Los Angeles"]},
                "clv": {"enabled": true, "min": 0.75, "max": 1.0},
                "aov": {"enabled": false},
                ...
            }
        }
    
    Returns:
        {
            "final_size": 1158,
            "final_avg_clv": 0.86,
            "final_avg_cart_value": 168.50,
            "filters_applied": [
                {"name": "Location Filter", "size": 1463, "change": "-48.6%"},
                {"name": "Cart Value Filter", "size": 1158, "change": "-20.8%"}
            ]
        }
    """
    try:
        data = request.get_json()
        coo = CampaignObjectiveObject(**data['campaign_objective_object'])
        filters = data['filters']
        
        preview = segment_service.preview_standard_filters(coo, filters)
        
        return jsonify(preview), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/segments/create-with-filters', methods=['POST'])
def create_segment_with_filters():
    """
    Create a segment with both standard filters AND trigger filter
    
    Request Body:
        {
            "campaign_objective": "...",
            "standard_filters": { ... },
            "trigger": "personalized_discount_offer" or null
        }
    """
    try:
        data = request.get_json()
        
        result = segment_service.create_segment_with_filters(
            campaign_objective=data['campaign_objective'],
            standard_filters=data.get('standard_filters', {}),
            trigger=data.get('trigger')
        )
        
        return jsonify(result.model_dump()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Backend Service Implementation

```python
# backend/services/segment_service.py

def preview_standard_filters(
    self, 
    coo: CampaignObjectiveObject, 
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Preview impact of standard filters without executing full segment creation
    """
    # Build base query
    base_query = self.query_builder.build_segment_query(coo, limit=None)
    base_data = self.bigquery_service.query(base_query)
    
    starting_size = len(base_data)
    current_data = base_data.copy()
    filters_applied = []
    
    # Apply each filter sequentially
    if filters.get('location', {}).get('enabled'):
        cities = filters['location']['cities']
        if cities:
            current_data = current_data[current_data['location_city'].isin(cities)]
            filters_applied.append({
                'name': 'Location Filter',
                'size': len(current_data),
                'change': f"{((len(current_data) - starting_size) / starting_size * 100):.1f}%"
            })
    
    if filters.get('clv', {}).get('enabled'):
        min_clv = filters['clv']['min']
        max_clv = filters['clv']['max']
        prev_size = len(current_data)
        current_data = current_data[
            (current_data['clv_score'] >= min_clv) & 
            (current_data['clv_score'] <= max_clv)
        ]
        if len(current_data) != prev_size:
            filters_applied.append({
                'name': 'CLV Filter',
                'size': len(current_data),
                'change': f"{((len(current_data) - prev_size) / prev_size * 100):.1f}%"
            })
    
    if filters.get('cartValue', {}).get('enabled') and 'cart_value' in current_data.columns:
        min_cart = filters['cartValue']['min']
        max_cart = filters['cartValue']['max']
        prev_size = len(current_data)
        current_data = current_data[
            (current_data['cart_value'] >= min_cart) & 
            (current_data['cart_value'] <= max_cart)
        ]
        if len(current_data) != prev_size:
            filters_applied.append({
                'name': 'Cart Value Filter',
                'size': len(current_data),
                'change': f"{((len(current_data) - prev_size) / prev_size * 100):.1f}%"
            })
    
    # ... Apply other filters similarly
    
    return {
        'final_size': len(current_data),
        'final_avg_clv': float(current_data['clv_score'].mean()) if len(current_data) > 0 else 0,
        'final_avg_cart_value': float(current_data['cart_value'].mean()) if 'cart_value' in current_data.columns and len(current_data) > 0 else None,
        'filters_applied': filters_applied,
        'percentage_retained': (len(current_data) / starting_size * 100) if starting_size > 0 else 0
    }


def create_segment_with_filters(
    self,
    campaign_objective: str,
    standard_filters: Dict[str, Any],
    trigger: Optional[str] = None
) -> SegmentResponse:
    """
    Create segment with standard filters first, then optional trigger filter
    """
    # Step 1: Interpret campaign
    coo = self.intent_interpreter.interpret(campaign_objective)
    
    # Step 2: Build query with standard filters
    segment_query = self.query_builder.build_segment_query_with_standard_filters(
        coo, 
        standard_filters,
        trigger_filter=trigger
    )
    
    # Step 3: Execute query
    customer_df = self.bigquery_service.query(segment_query)
    
    # Step 4: Create segment response
    # ... (rest of segment creation logic)
```

### Query Builder Updates

```python
# backend/models/query_builder.py

def build_segment_query_with_standard_filters(
    self,
    coo: CampaignObjectiveObject,
    standard_filters: Dict[str, Any],
    trigger_filter: Optional[str] = None
) -> str:
    """
    Build query with standard filters added to WHERE clause
    """
    # Build base query parts
    select_clause = self._build_select_clause(coo)
    from_clause = self._build_from_clause(coo)
    where_conditions = []
    
    # Add AI-driven campaign criteria
    base_where = self._build_where_clause(coo, None)
    if base_where:
        # Extract conditions from base WHERE clause
        where_conditions.extend(base_where.replace('WHERE', '').strip().split('\n  AND '))
    
    # Add standard filter conditions
    if standard_filters.get('location', {}).get('enabled'):
        cities = standard_filters['location']['cities']
        if cities:
            city_list = "', '".join(cities)
            where_conditions.append(f"c.location_city IN ('{city_list}')")
    
    if standard_filters.get('clv', {}).get('enabled'):
        min_clv = standard_filters['clv']['min']
        max_clv = standard_filters['clv']['max']
        where_conditions.append(f"c.clv_score >= {min_clv}")
        where_conditions.append(f"c.clv_score <= {max_clv}")
    
    if standard_filters.get('cartValue', {}).get('enabled'):
        min_cart = standard_filters['cartValue']['min']
        max_cart = standard_filters['cartValue']['max']
        where_conditions.append(f"ac.cart_value >= {min_cart}")
        where_conditions.append(f"ac.cart_value <= {max_cart}")
    
    # Add trigger filter if specified
    if trigger_filter:
        uplift_scores = {trigger_filter: Config.DEFAULT_UPLIFT_THRESHOLD}
        trigger_where = self._build_trigger_where_clause(trigger_filter, uplift_scores)
        if trigger_where:
            where_conditions.extend(trigger_where)
    
    # Combine all conditions
    where_clause = "WHERE\n  " + "\n  AND ".join(where_conditions) if where_conditions else ""
    
    order_clause = self._build_order_clause(coo)
    
    query = f"""
{select_clause}
{from_clause}
{where_clause}
{order_clause}
"""
    
    return query.strip()
```

---

## 📋 Summary

### Complete Flow:
1. **Campaign Input** → AI parses objective
2. **Full Eligible Segment** → Shows AI-identified criteria (e.g., high-value, 48hrs)
   - Option: Proceed, Apply Standard Filters, or Apply Trigger
3. **Standard Filters (Optional)** → Location, CLV, AOV, Behavioral, Timing, Acquisition
   - All filters optional
   - Real-time preview shows impact
   - Can skip this step entirely
4. **Trigger Filter (Optional)** → AI-recommended triggers
   - Includes "No Filter" option
   - Shows estimated segment size
   - Can skip this step entirely
5. **Final Activation** → Export/Activate filtered segment

### Benefits:
- ✅ Step-by-step, not overwhelming
- ✅ Every filter is optional
- ✅ Real-time preview of impact
- ✅ Location is prominent (most requested)
- ✅ Combines AI intelligence + manual control
- ✅ Clear progression from broad → refined

**Ready to implement?** I can start with the frontend filter UI and then add the backend preview logic!
