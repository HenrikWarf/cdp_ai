/**
 * Campaign Templates and Builder Configuration
 * Pre-defined campaigns and options for guided campaign builder
 */

// 15 Pre-defined Campaign Templates organized into 5 groups
export const CAMPAIGN_TEMPLATES = {
    'abandoned_cart': {
        title: 'Abandoned Cart Recovery',
        campaigns: [
            {
                id: 'cart_discount',
                title: 'Standard Cart Recovery',
                description: 'Recover abandoned carts with personalized discount offers',
                fullObjective: 'Recover abandoned furniture carts from the last 48 hours with a personalized 15% discount to increase conversion by 25%'
            },
            {
                id: 'cart_shipping',
                title: 'High-Value Cart Recovery',
                description: 'Target high-value abandoned carts with free shipping',
                fullObjective: 'Recover high-value abandoned carts over $500 in the last 72 hours with free shipping to boost conversion by 30% and reduce cart abandonment'
            },
            {
                id: 'cart_urgency',
                title: 'Urgency-Based Cart Recovery',
                description: 'Create urgency with limited-time offers for abandoned carts',
                fullObjective: 'Re-engage customers who abandoned their furniture carts in the last 24 hours using scarcity messaging (limited stock alerts) to drive 20% conversion increase'
            }
        ]
    },
    'winback': {
        title: 'Win-Back Campaigns',
        campaigns: [
            {
                id: 'winback_exclusive',
                title: 'Lapsed Customer Win-Back',
                description: 'Re-engage customers who haven\'t purchased recently',
                fullObjective: 'Win back customers with high churn risk who haven\'t purchased in 90 days using exclusive comeback offers with 20% discount to bring back 15% of lapsed customers'
            },
            {
                id: 'winback_new_products',
                title: 'Dormant Customer Reactivation',
                description: 'Show new products to inactive customers',
                fullObjective: 'Reactivate dormant customers who haven\'t engaged in 6 months by showcasing new Living Room and Bedroom furniture collections with personalized content to achieve 12% reactivation rate'
            },
            {
                id: 'winback_vip',
                title: 'High-Value Customer Win-Back',
                description: 'Bring back high CLV customers with VIP treatment',
                fullObjective: 'Re-engage high CLV customers (80%+) who haven\'t purchased in 60 days with exclusive VIP early access to new collections and free white glove delivery to retain 25% of at-risk premium customers'
            }
        ]
    },
    'cross_sell': {
        title: 'Cross-Sell & Upsell',
        campaigns: [
            {
                id: 'crosssell_complementary',
                title: 'Recent Buyer Cross-Sell',
                description: 'Recommend complementary items to recent purchasers',
                fullObjective: 'Recommend complementary furniture items to customers who purchased sofas in the last 30 days (suggest coffee tables, side tables, rugs) to drive cross-sell revenue by 20%'
            },
            {
                id: 'crosssell_category',
                title: 'Category Expansion',
                description: 'Encourage customers to explore new product categories',
                fullObjective: 'Expand product adoption by targeting Bedroom furniture buyers to explore Living Room collections with bundled discount offers to increase average customer value by 25%'
            },
            {
                id: 'crosssell_bundle',
                title: 'Bundle Opportunities',
                description: 'Create attractive bundles for complementary products',
                fullObjective: 'Increase order value by offering curated room bundles (Bedroom Set: bed frame + nightstands + dresser) to customers browsing individual items with 15% bundle discount to boost AOV by 30%'
            }
        ]
    },
    'new_customer': {
        title: 'New Customer Campaigns',
        campaigns: [
            {
                id: 'welcome_discount',
                title: 'Welcome Campaign',
                description: 'Welcome new customers with first purchase incentive',
                fullObjective: 'Welcome new customers acquired in the last 7 days with 10% first purchase discount on any furniture item to encourage first purchase and boost repeat rate by 30%'
            },
            {
                id: 'onboarding_content',
                title: 'Onboarding Nurture',
                description: 'Guide new customers with helpful content and tips',
                fullObjective: 'Nurture new customers in their first 14 days with personalized room planning guides and style inspiration content to increase engagement by 40% and drive first purchase within 21 days'
            },
            {
                id: 'early_loyalty',
                title: 'Early Loyalty Incentive',
                description: 'Build loyalty early with shipping benefits',
                fullObjective: 'Encourage second purchase from customers who bought once in last 30 days by offering free shipping on their next order to increase repeat purchase rate by 25%'
            }
        ]
    },
    'vip_highvalue': {
        title: 'VIP/High-Value Campaigns',
        campaigns: [
            {
                id: 'vip_launch',
                title: 'Exclusive Product Launch',
                description: 'Give premium customers first access to new products',
                fullObjective: 'Target high CLV customers (75%+) in major metro areas with exclusive 48-hour early access to new premium furniture collections using exclusivity messaging to drive 20% conversion and strengthen brand loyalty'
            },
            {
                id: 'vip_retention',
                title: 'Premium Customer Retention',
                description: 'Reward and retain your best customers',
                fullObjective: 'Retain high-value customers with CLV above 80% using loyalty rewards (points program, free assembly, extended warranty) to reduce churn by 30% and increase lifetime value'
            },
            {
                id: 'vip_sale_access',
                title: 'VIP Early Sale Access',
                description: 'Reward loyal customers with pre-sale access',
                fullObjective: 'Reward loyal customers with 3+ purchases in the last year with exclusive 24-hour early access to seasonal sales and additional 5% VIP discount to increase purchase frequency by 35%'
            }
        ]
    },
    'product_specific': {
        title: 'Product & Category Campaigns',
        campaigns: [
            {
                id: 'living_room_cross_sell',
                title: 'Living Room Cross-Sell',
                description: 'Cross-sell complementary living room items',
                fullObjective: 'Target customers with high living room affinity who purchased sofas in the last 60 days to recommend complementary items (coffee tables, side tables, lamps) with 15% bundle discount to increase AOV by 30%'
            },
            {
                id: 'bedroom_collection',
                title: 'Complete Bedroom Campaign',
                description: 'Encourage complete room purchases',
                fullObjective: 'Target bedroom furniture buyers with curated complete bedroom collections (bed + nightstands + dresser + lighting) using bundle pricing with 20% discount to boost conversion by 25% and increase average order value'
            },
            {
                id: 'office_wfh',
                title: 'Home Office Upgrade',
                description: 'Target work-from-home customers',
                fullObjective: 'Target customers with high office furniture affinity to upgrade their home office setup with premium desks, ergonomic chairs, and storage solutions using content marketing about productivity to drive 20% conversion'
            },
            {
                id: 'seasonal_outdoor',
                title: 'Seasonal Outdoor Launch',
                description: 'Promote outdoor furniture seasonally',
                fullObjective: 'Target customers with cross-category shopping behavior and premium price preferences to launch new outdoor patio collections with early-bird 15% discount to achieve 25% conversion in spring season'
            },
            {
                id: 'lighting_refresh',
                title: 'Lighting & Ambiance',
                description: 'Cross-sell lighting to recent buyers',
                fullObjective: 'Target customers who purchased living room or bedroom furniture in last 90 days with personalized lighting recommendations (floor lamps, table lamps, smart lighting) to complete their room setup and increase repeat purchase rate by 30%'
            }
        ]
    }
};

// Campaign Builder Configuration
export const BUILDER_CONFIG = {
    goals: [
        { value: 'conversion', label: 'Increase Conversion', description: 'Turn browsers into buyers' },
        { value: 'retention', label: 'Improve Retention', description: 'Keep customers coming back' },
        { value: 'acquisition', label: 'Acquire New Customers', description: 'Grow your customer base' },
        { value: 'winback', label: 'Win Back Customers', description: 'Re-engage lapsed customers' },
        { value: 'cross_sell', label: 'Cross-Sell Products', description: 'Increase order value' },
        { value: 'upsell', label: 'Upsell Premium Items', description: 'Move customers to higher tiers' },
        { value: 'engagement', label: 'Boost Engagement', description: 'Increase customer activity' },
        { value: 'loyalty', label: 'Build Loyalty', description: 'Create brand advocates' }
    ],
    
    triggers: [
        { value: 'discount', label: 'Discount Offer', description: 'Percentage or dollar off' },
        { value: 'free_shipping', label: 'Free Shipping', description: 'Waive delivery fees' },
        { value: 'exclusivity', label: 'Exclusive Access', description: 'VIP-only offers' },
        { value: 'scarcity', label: 'Limited Availability', description: 'Low stock urgency' },
        { value: 'social_proof', label: 'Social Proof', description: 'Reviews and testimonials' },
        { value: 'gift_with_purchase', label: 'Gift with Purchase', description: 'Free bonus item' },
        { value: 'cashback', label: 'Cashback/Rewards', description: 'Points or money back' },
        { value: 'bundling', label: 'Bundle Discount', description: 'Multi-item savings' },
        { value: 'content', label: 'Helpful Content', description: 'Guides and inspiration' },
        { value: 'time_limited', label: 'Flash Sale', description: 'Limited time offer' }
    ],
    
    productCategories: [
        { value: 'living_room', label: 'Living Room', examples: 'Sofas, Coffee Tables, TV Stands' },
        { value: 'bedroom', label: 'Bedroom', examples: 'Beds, Wardrobes, Nightstands' },
        { value: 'kitchen_dining', label: 'Kitchen & Dining', examples: 'Dining Tables, Chairs, Bar Stools' },
        { value: 'office', label: 'Office', examples: 'Desks, Office Chairs, Storage' },
        { value: 'outdoor', label: 'Outdoor', examples: 'Patio Sets, Garden Furniture' },
        { value: 'lighting', label: 'Lighting', examples: 'Lamps, Ceiling Lights' },
        { value: 'storage', label: 'Storage & Organization', examples: 'Shelving, Storage Boxes' },
        { value: 'textiles', label: 'Textiles', examples: 'Curtains, Cushions, Bedding' },
        { value: 'bathroom', label: 'Bathroom', examples: 'Cabinets, Mirrors, Accessories' },
        { value: 'all_categories', label: 'All Products', examples: 'Any furniture category' }
    ],
    
    // Template for generating campaign objectives from builder selections
    generateObjective: (goal, trigger, productCategory) => {
        const templates = {
            conversion: `Increase conversion for ${productCategory} products by 20% using ${trigger} to drive more purchases from engaged browsers`,
            retention: `Improve retention of ${productCategory} customers by 25% with ${trigger} to encourage repeat purchases within 60 days`,
            acquisition: `Acquire new customers interested in ${productCategory} with ${trigger} to grow customer base by 30% this quarter`,
            winback: `Win back lapsed ${productCategory} customers who haven't purchased in 90 days using ${trigger} to reactivate 15% of dormant customers`,
            cross_sell: `Cross-sell complementary ${productCategory} items to recent buyers with ${trigger} to increase average order value by 20%`,
            upsell: `Upsell premium ${productCategory} collections to mid-tier customers using ${trigger} to boost customer lifetime value by 25%`,
            engagement: `Boost engagement with ${productCategory} content and offers using ${trigger} to increase site visits by 40%`,
            loyalty: `Build loyalty among ${productCategory} customers with ${trigger} rewards to increase repeat purchase rate by 30%`
        };
        
        return templates[goal] || `Improve ${goal} for ${productCategory} using ${trigger}`;
    }
};

