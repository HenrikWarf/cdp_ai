"""
Overview Dashboard Routes
Provides aggregated statistics and insights for the overview dashboard
"""

from flask import Blueprint, jsonify, request
from backend.services.bigquery_service import BigQueryService
from backend.config import Config
from datetime import datetime, timedelta

overview_bp = Blueprint('overview', __name__)
bigquery_service = BigQueryService()

# In-memory cache for overview statistics
_overview_cache = {
    'data': None,
    'timestamp': None,
    'ttl_minutes': 10  # Cache for 10 minutes by default
}


@overview_bp.route('/stats', methods=['GET'])
def get_overview_stats():
    """
    Get overview dashboard statistics (with caching)
    
    Query Parameters:
    - refresh: Set to 'true' to bypass cache and fetch fresh data
    
    Returns comprehensive metrics including:
    - Total customers
    - Abandoned carts
    - Average CLV
    - At-risk customers
    - Geographic distribution
    - Value segments
    - Campaign opportunities
    - Behavioral insights
    - Data health metrics
    - cached: Boolean indicating if data was from cache
    - last_updated: ISO timestamp of when data was fetched
    """
    try:
        # Check if refresh is requested
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        # Check cache validity
        cache_valid = False
        if _overview_cache['data'] is not None and _overview_cache['timestamp'] is not None:
            cache_age = datetime.utcnow() - _overview_cache['timestamp']
            cache_valid = cache_age.total_seconds() < (_overview_cache['ttl_minutes'] * 60)
        
        # Return cached data if valid and not forcing refresh
        if cache_valid and not force_refresh:
            print(f"📦 Returning cached overview data (age: {cache_age.total_seconds():.0f}s)")
            response = _overview_cache['data'].copy()
            response['cached'] = True
            response['last_updated'] = _overview_cache['timestamp'].isoformat()
            return jsonify(response)
        
        # Fetch fresh data
        if force_refresh:
            print("\n🔄 Force refresh requested - fetching fresh overview statistics...")
        else:
            print("\n📊 Cache expired or empty - fetching overview statistics...")
        
        # Fetch each section with individual error handling
        metrics = None
        geo_dist = None
        value_segs = None
        opps = None
        insights = None
        health = None
        
        try:
            print("  → Fetching key metrics...")
            metrics = get_key_metrics()
            print("  ✓ Key metrics retrieved")
        except Exception as e:
            print(f"  ✗ Key metrics failed: {str(e)}")
            metrics = {'error': str(e)}
        
        try:
            print("  → Fetching geographic distribution...")
            geo_dist = get_geographic_distribution()
            print("  ✓ Geographic distribution retrieved")
        except Exception as e:
            print(f"  ✗ Geographic distribution failed: {str(e)}")
            geo_dist = {}
        
        try:
            print("  → Fetching value segments...")
            value_segs = get_value_segments()
            print("  ✓ Value segments retrieved")
        except Exception as e:
            print(f"  ✗ Value segments failed: {str(e)}")
            value_segs = {}
        
        try:
            print("  → Fetching campaign opportunities...")
            opps = get_campaign_opportunities()
            print("  ✓ Campaign opportunities retrieved")
        except Exception as e:
            print(f"  ✗ Campaign opportunities failed: {str(e)}")
            opps = []
        
        try:
            print("  → Fetching behavioral insights...")
            insights = get_behavioral_insights()
            print("  ✓ Behavioral insights retrieved")
        except Exception as e:
            print(f"  ✗ Behavioral insights failed: {str(e)}")
            insights = []
        
        try:
            print("  → Fetching data health...")
            health = get_data_health()
            print("  ✓ Data health retrieved")
        except Exception as e:
            print(f"  ✗ Data health failed: {str(e)}")
            health = {}
        
        stats = {
            'metrics': metrics,
            'geographic_distribution': geo_dist,
            'value_segments': value_segs,
            'opportunities': opps,
            'behavioral_insights': insights,
            'data_health': health,
            'cached': False,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Update cache
        _overview_cache['data'] = stats.copy()
        _overview_cache['timestamp'] = datetime.utcnow()
        
        print(f"✅ Overview statistics compiled successfully and cached (TTL: {_overview_cache['ttl_minutes']} min)")
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Error fetching overview stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def get_key_metrics():
    """Get top-level key metrics"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    # Total customers
    query = f"""
    SELECT COUNT(*) as total
    FROM `{project}.{dataset}.customers`
    """
    total_customers = bigquery_service.query(query)['total'].iloc[0]
    
    # Abandoned carts (last 7 days)
    query = f"""
    SELECT COUNT(*) as total
    FROM `{project}.{dataset}.abandoned_carts`
    WHERE status = 'abandoned'
      AND CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """
    abandoned_carts = bigquery_service.query(query)['total'].iloc[0]
    
    # Average CLV
    query = f"""
    SELECT AVG(clv_score) as avg_clv
    FROM `{project}.{dataset}.customers`
    """
    avg_clv = bigquery_service.query(query)['avg_clv'].iloc[0]
    
    # At-risk customers (high churn probability)
    query = f"""
    SELECT COUNT(*) as total
    FROM `{project}.{dataset}.customer_scores`
    WHERE churn_probability_score > 0.6
    """
    at_risk = bigquery_service.query(query)['total'].iloc[0]
    
    return {
        'total_customers': int(total_customers),
        'abandoned_carts_7d': int(abandoned_carts),
        'avg_clv_score': float(avg_clv),
        'at_risk_customers': int(at_risk)
    }


def get_geographic_distribution():
    """Get geographic distribution of customers"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    query = f"""
    SELECT 
      location_country,
      COUNT(*) as customer_count
    FROM `{project}.{dataset}.customers`
    GROUP BY location_country
    ORDER BY customer_count DESC
    LIMIT 10
    """
    
    result = bigquery_service.query(query)
    return {str(k): int(v) for k, v in zip(result['location_country'], result['customer_count'])}


def get_value_segments():
    """Get customer distribution by value segments"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    query = f"""
    SELECT
      CASE
        WHEN clv_score >= 0.75 THEN 'high'
        WHEN clv_score >= 0.50 THEN 'medium'
        ELSE 'low'
      END as segment,
      COUNT(*) as count
    FROM `{project}.{dataset}.customers`
    GROUP BY segment
    """
    
    result = bigquery_service.query(query)
    return {str(k): int(v) for k, v in zip(result['segment'], result['count'])}


def get_campaign_opportunities():
    """Identify top campaign opportunities"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    opportunities = []
    
    # 1. Abandoned Cart Recovery
    query = f"""
    SELECT COUNT(*) as count
    FROM `{project}.{dataset}.abandoned_carts`
    WHERE status = 'abandoned'
      AND CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """
    result = bigquery_service.query(query)
    abandoned_count = int(result['count'].iloc[0])
    
    if abandoned_count > 0:
        opportunities.append({
            'icon': '🛒',
            'title': 'Abandoned Cart Recovery',
            'description': 'Recent carts waiting to be recovered',
            'segment_size': int(abandoned_count),
            'potential_uplift': 0.25
        })
    
    # 2. Win-Back High-Value Customers
    query = f"""
    SELECT COUNT(*) as count
    FROM `{project}.{dataset}.customer_scores` cs
    INNER JOIN `{project}.{dataset}.customers` c ON cs.customer_id = c.customer_id
    WHERE cs.churn_probability_score > 0.6
      AND c.clv_score >= 0.70
    """
    result = bigquery_service.query(query)
    lapsed_high_value = int(result['count'].iloc[0])
    
    if lapsed_high_value > 0:
        opportunities.append({
            'icon': '💎',
            'title': 'Win-Back High-Value Customers',
            'description': 'At-risk customers with high lifetime value',
            'segment_size': int(lapsed_high_value),
            'potential_uplift': 0.30
        })
    
    # 3. New Customer Onboarding
    query = f"""
    SELECT COUNT(*) as count
    FROM `{project}.{dataset}.customers`
    WHERE CAST(creation_date AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """
    result = bigquery_service.query(query)
    new_customers = int(result['count'].iloc[0])
    
    if new_customers > 0:
        opportunities.append({
            'icon': '✨',
            'title': 'New Customer Onboarding',
            'description': 'Recently acquired customers ready for engagement',
            'segment_size': int(new_customers),
            'potential_uplift': 0.20
        })
    
    # 4. Retention Campaign
    query = f"""
    SELECT COUNT(DISTINCT customer_id) as count
    FROM `{project}.{dataset}.transactions`
    WHERE CAST(timestamp AS TIMESTAMP) BETWEEN 
      TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND
      TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """
    result = bigquery_service.query(query)
    retention_opportunity = int(result['count'].iloc[0])
    
    if retention_opportunity > 0:
        opportunities.append({
            'icon': '🔄',
            'title': 'Retention Campaign',
            'description': 'Customers who haven\'t purchased recently',
            'segment_size': int(retention_opportunity),
            'potential_uplift': 0.18
        })
    
    return opportunities


def get_behavioral_insights():
    """Get behavioral insights from recent customer activity"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    insights = []
    
    # Active customers (last 7 days)
    query = f"""
    SELECT COUNT(DISTINCT customer_id) as count
    FROM `{project}.{dataset}.behavioral_events`
    WHERE CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    """
    result = bigquery_service.query(query)
    active_customers = int(result['count'].iloc[0])
    
    insights.append({
        'icon': '🔥',
        'label': 'Active Customers (7d)',
        'value': f"{int(active_customers):,}",
        'description': 'Customers with recent activity'
    })
    
    # Avg events per customer
    query = f"""
    SELECT 
      COUNT(*) / COUNT(DISTINCT customer_id) as avg_events
    FROM `{project}.{dataset}.behavioral_events`
    WHERE CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """
    result = bigquery_service.query(query)
    avg_events = float(result['avg_events'].iloc[0])
    
    insights.append({
        'icon': '📊',
        'label': 'Avg Engagement (30d)',
        'value': f"{float(avg_events):.1f}",
        'description': 'Events per customer'
    })
    
    # Top product category
    query = f"""
    SELECT 
      product_category,
      COUNT(*) as count
    FROM `{project}.{dataset}.behavioral_events`
    WHERE CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY product_category
    ORDER BY count DESC
    LIMIT 1
    """
    result = bigquery_service.query(query)
    if len(result) > 0:
        top_category = result['product_category'].iloc[0]
        insights.append({
            'icon': '🏆',
            'label': 'Top Category (7d)',
            'value': top_category,
            'description': 'Most viewed this week'
        })
    
    return insights


def get_data_health():
    """Get data health metrics"""
    dataset = Config.BIGQUERY_DATASET
    project = Config.GOOGLE_CLOUD_PROJECT
    
    # Total events
    query = f"""
    SELECT COUNT(*) as total
    FROM `{project}.{dataset}.behavioral_events`
    """
    result = bigquery_service.query(query)
    total_events = int(result['total'].iloc[0])
    
    # Latest event timestamp
    query = f"""
    SELECT MAX(timestamp) as latest
    FROM `{project}.{dataset}.behavioral_events`
    """
    result = bigquery_service.query(query)
    latest_event = result['latest'].iloc[0]
    
    # Customer coverage (% of customers with events)
    query = f"""
    SELECT 
      (COUNT(DISTINCT be.customer_id) * 100.0 / (SELECT COUNT(*) FROM `{project}.{dataset}.customers`)) as coverage
    FROM `{project}.{dataset}.behavioral_events` be
    """
    result = bigquery_service.query(query)
    coverage = float(result['coverage'].iloc[0]) / 100.0
    
    return {
        'total_events': int(total_events),
        'latest_event': str(latest_event),
        'data_freshness': 'Real-time',
        'customer_coverage': float(coverage)
    }

