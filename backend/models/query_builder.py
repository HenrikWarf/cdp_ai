"""
Dynamic SQL query builder for segment generation
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from backend.api.schemas import CampaignObjectiveObject
from backend.utils.helpers import parse_time_constraint, sanitize_sql_identifier
from backend.config import Config


class QueryBuilder:
    """
    Builds dynamic SQL queries for customer segmentation based on
    Campaign Objective Objects and uplift scores
    """
    
    def __init__(self, dataset_id: str = None):
        """
        Initialize query builder
        
        Args:
            dataset_id: BigQuery dataset ID
        """
        self.dataset_id = dataset_id or Config.BIGQUERY_DATASET
    
    def build_segment_query(
        self,
        coo: CampaignObjectiveObject,
        uplift_scores: Optional[Dict[str, float]] = None,
        limit: Optional[int] = None
    ) -> str:
        """
        Build a SQL query to fetch customer segment
        
        Args:
            coo: Campaign Objective Object
            uplift_scores: Dictionary of uplift score thresholds for different triggers
            limit: Optional limit on number of results
        
        Returns:
            SQL query string
        """
        # Build SELECT clause
        select_clause = self._build_select_clause(coo)
        
        # Build FROM clause with joins
        from_clause = self._build_from_clause(coo)
        
        # Build WHERE clause with conditions
        where_clause = self._build_where_clause(coo, uplift_scores)
        
        # Build ORDER BY clause
        order_clause = self._build_order_clause(coo)
        
        # Combine all parts
        query = f"""
{select_clause}
{from_clause}
{where_clause}
{order_clause}
"""
        
        if limit:
            query += f"\nLIMIT {limit}"
        
        return query.strip()
    
    def _build_select_clause(self, coo: CampaignObjectiveObject) -> str:
        """Build the SELECT clause"""
        base_fields = [
            "c.customer_id",
            "c.email_address",
            "c.first_name",
            "c.location_city",
            "c.location_country",
            "c.clv_score",
            "cs.discount_sensitivity_score",
            "cs.free_shipping_sensitivity_score",
            "cs.exclusivity_seeker_flag",
            "cs.social_proof_affinity",
            "cs.churn_probability_score",
            "cs.content_engagement_score",
            "cs.favorite_category",
            "cs.secondary_category",
            "cs.price_tier_preference"
        ]
        
        # Add behavior-specific fields
        if coo.target_behavior == "abandoned_cart":
            base_fields.extend([
                "ac.cart_id as abandoned_cart_id",
                "ac.cart_value",
                "ac.items as cart_items",
                "ac.timestamp as cart_abandoned_at"
            ])
        
        return "SELECT\n  " + ",\n  ".join(base_fields)
    
    def _build_from_clause(self, coo: CampaignObjectiveObject) -> str:
        """Build the FROM clause with appropriate joins"""
        dataset = self.dataset_id
        
        from_parts = [
            f"FROM `{dataset}.customers` c",
            f"INNER JOIN `{dataset}.customer_scores` cs ON c.customer_id = cs.customer_id"
        ]
        
        # Add behavior-specific joins
        if coo.target_behavior == "abandoned_cart":
            from_parts.append(
                f"INNER JOIN `{dataset}.abandoned_carts` ac ON c.customer_id = ac.customer_id"
            )
        
        # Note: We don't join transactions here to avoid duplicate rows
        # Transaction data is already reflected in customer_scores (e.g., CLV)
        
        return "\n".join(from_parts)
    
    def _build_where_clause(
        self,
        coo: CampaignObjectiveObject,
        uplift_scores: Optional[Dict[str, float]] = None
    ) -> str:
        """Build the WHERE clause with all conditions"""
        conditions = []
        
        # Behavior-based conditions
        if coo.target_behavior:
            if coo.target_behavior == "abandoned_cart":
                # Abandoned cart specific conditions
                cutoff = datetime.utcnow() - timedelta(days=7)
                conditions.append(
                    f"TIMESTAMP(ac.timestamp) > TIMESTAMP('{cutoff.isoformat()}')"
                )
                conditions.append("ac.status = 'abandoned'")
                print(f"   🕐 Abandoned cart filter: last 7 days")
                
            elif coo.target_behavior == "lapsed_customer":
                # Lapsed customer = high churn probability
                conditions.append("cs.churn_probability_score > 0.6")
                print(f"   👋 Lapsed customer filter: churn_probability > 0.6")
                
            elif coo.target_behavior in ["high_engagement", "active_customer"]:
                # High engagement customers
                conditions.append("cs.content_engagement_score > 0.7")
                print(f"   🔥 High engagement filter: content_engagement > 0.7")
            
            elif coo.target_behavior == "cross_sell":
                # Cross-sell: customers who purchased recently
                conditions.append(f"""
                    EXISTS (
                        SELECT 1 FROM `{self.dataset_id}.transactions` t
                        WHERE t.customer_id = c.customer_id
                        AND CAST(t.timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                    )
                """)
                print(f"   🔀 Cross-sell filter: recent purchasers (last 30 days)")
            
            elif coo.target_behavior in ["new_customer", "acquisition"]:
                # New customers - use time_constraint if provided, otherwise default to 7 days
                days_interval = 7  # default
                if coo.time_constraint:
                    # Parse common time constraints
                    time_str = coo.time_constraint.lower()
                    if 'quarter' in time_str or '90' in time_str:
                        days_interval = 90
                    elif '30' in time_str or 'month' in time_str:
                        days_interval = 30
                    elif '14' in time_str or 'two_week' in time_str:
                        days_interval = 14
                    elif '7' in time_str or 'week' in time_str:
                        days_interval = 7
                
                conditions.append(f"CAST(c.creation_date AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days_interval} DAY)")
                print(f"   ✨ New customer filter: acquired in last {days_interval} days")
            
            elif coo.target_behavior in ["retention", "repeat_purchase"]:
                # At-risk retention: purchased 30-90 days ago, might not come back
                conditions.append(f"""
                    c.customer_id IN (
                        SELECT DISTINCT customer_id 
                        FROM `{self.dataset_id}.transactions`
                        WHERE CAST(timestamp AS TIMESTAMP) BETWEEN 
                            TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND
                            TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                    )
                """)
                print(f"   🔄 Retention filter: last purchase 30-90 days ago")
            
            elif coo.target_behavior in ["reactivation", "dormant"]:
                # Reactivation: customers at risk of churning (high churn probability)
                # This is broader than "no activity" and more actionable
                conditions.append("cs.churn_probability_score > 0.6")
                print(f"   💤 Reactivation filter: churn_probability > 0.6")
        
        # CLV/Value-based conditions for high-value shoppers
        if coo.target_subgroup and "high_value" in coo.target_subgroup.lower():
            conditions.append("c.clv_score >= 0.75")  # Top 25%
            print(f"   💰 High-value filter: clv_score >= 0.75")
        
        # Win-back campaign specific conditions
        if coo.campaign_goal == "win_back" and coo.target_behavior == "lapsed_customer":
            conditions.append("cs.exclusivity_seeker_flag = true")
            print(f"   🎁 Win-back filter: exclusivity_seeker_flag = true")
        
        # Product affinity filtering
        # Look for product categories in target_subgroup or target_behavior
        product_filters = self._extract_product_affinity_filters(coo)
        if product_filters:
            conditions.extend(product_filters)
        
        # Uplift score conditions based on selected trigger
        if uplift_scores:
            # Get the first (and only) trigger from uplift_scores dict
            trigger_name = list(uplift_scores.keys())[0]
            threshold = list(uplift_scores.values())[0]
            
            # Sanitize trigger name for SQL field lookup
            intervention = sanitize_sql_identifier(trigger_name)
            
            # Map trigger name to score field
            score_mapping = {
                'personalized_discount_offer': 'discount_sensitivity_score',
                'discount': 'discount_sensitivity_score',
                'free_shipping': 'free_shipping_sensitivity_score',
                'free_expedited_shipping': 'free_shipping_sensitivity_score',
                'scarcity': 'discount_sensitivity_score',  # Scarcity works on price-sensitive customers
                'exclusivity': 'exclusivity_seeker_flag',  # Boolean field
                'social_proof': 'social_proof_affinity'  # Separate affinity score
            }
            
            score_field = score_mapping.get(intervention, 'discount_sensitivity_score')
            
            # Handle boolean fields (like exclusivity_seeker_flag)
            if score_field == 'exclusivity_seeker_flag':
                conditions.append(f"cs.{score_field} = true")
                print(f"   🎯 Trigger filter: {trigger_name} -> {score_field} = true")
            else:
                conditions.append(f"cs.{score_field} > {threshold}")
                print(f"   🎯 Trigger filter: {trigger_name} -> {score_field} > {threshold}")
        
        # Cart value conditions ONLY for abandoned cart campaigns
        if coo.target_behavior == "abandoned_cart":
            # Target carts with above-average value
            conditions.append(
                "ac.cart_value > (SELECT AVG(cart_value) FROM `{}.abandoned_carts`)".format(
                    self.dataset_id
                )
            )
            print(f"   🛒 Cart value filter: above average")
        
        # Combine all conditions
        if conditions:
            return "WHERE\n  " + "\n  AND ".join(conditions)
        else:
            return ""
    
    def _build_order_clause(self, coo: CampaignObjectiveObject) -> str:
        """Build the ORDER BY clause"""
        # Order by CLV score and uplift potential
        return "ORDER BY c.clv_score DESC, cs.discount_sensitivity_score DESC"
    
    def build_metadata_query(self, segment_query: str) -> str:
        """
        Build a query to get metadata about the segment
        
        Args:
            segment_query: The main segment query
        
        Returns:
            SQL query for metadata
        """
        return f"""
WITH segment_data AS (
  {segment_query}
)
SELECT
  COUNT(*) as segment_size,
  AVG(clv_score) as avg_clv_score,
  AVG(cart_value) as avg_cart_value,
  AVG(discount_sensitivity_score) as avg_discount_sensitivity,
  AVG(free_shipping_sensitivity_score) as avg_shipping_sensitivity,
  APPROX_TOP_COUNT(location_city, 5) as top_cities
FROM segment_data
"""
    
    def build_campaign_history_query(self, customer_ids: List[str], intervention: str) -> str:
        """
        Build a query to fetch campaign history for uplift model training
        
        Args:
            customer_ids: List of customer IDs
            intervention: The intervention/trigger type
        
        Returns:
            SQL query string
        """
        customer_ids_str = "', '".join(customer_ids[:1000])  # Limit for safety
        
        return f"""
SELECT
  ch.customer_id,
  ch.campaign_id,
  ch.trigger_type,
  ch.converted,
  ch.control_group,
  ch.timestamp,
  c.clv_score,
  cs.discount_sensitivity_score,
  cs.free_shipping_sensitivity_score
FROM `{self.dataset_id}.campaign_history` ch
INNER JOIN `{self.dataset_id}.customer_scores` cs 
  ON ch.customer_id = cs.customer_id
INNER JOIN `{self.dataset_id}.customers` c
  ON ch.customer_id = c.customer_id
WHERE ch.customer_id IN ('{customer_ids_str}')
  AND ch.trigger_type = '{intervention}'
ORDER BY ch.timestamp DESC
"""
    
    def _extract_product_affinity_filters(self, coo: CampaignObjectiveObject) -> List[str]:
        """
        Extract product affinity filters from campaign objective
        
        Args:
            coo: Campaign Objective Object
        
        Returns:
            List of SQL filter conditions
        """
        filters = []
        
        # Category mappings
        category_affinity_map = {
            'living_room': 'living_room_affinity',
            'living': 'living_room_affinity',
            'sofa': 'living_room_affinity',
            'bedroom': 'bedroom_affinity',
            'bed': 'bedroom_affinity',
            'kitchen': 'kitchen_dining_affinity',
            'dining': 'kitchen_dining_affinity',
            'office': 'office_affinity',
            'desk': 'office_affinity',
            'outdoor': 'outdoor_affinity',
            'patio': 'outdoor_affinity',
            'lighting': 'lighting_affinity',
            'lamp': 'lighting_affinity',
            'storage': 'storage_affinity',
            'textiles': 'textiles_affinity',
            'bathroom': 'bathroom_affinity',
            'decoration': 'decoration_affinity',
        }
        
        # Check target_subgroup for product mentions
        search_text = ""
        if coo.target_subgroup:
            search_text += coo.target_subgroup.lower() + " "
        if coo.target_behavior:
            search_text += coo.target_behavior.lower() + " "
        
        # Look for category keywords in the search text
        for keyword, affinity_col in category_affinity_map.items():
            if keyword in search_text:
                # Target customers with medium to high affinity (>= 0.3)
                filters.append(f"cs.{affinity_col} >= 0.3")
                print(f"   🏠 Product affinity filter: {affinity_col} >= 0.3")
                break  # Only apply one product filter per campaign
        
        # Check for cross-category shoppers
        if 'cross' in search_text or 'multiple' in search_text or 'various' in search_text:
            filters.append("cs.cross_category_shopper = true")
            print(f"   🔀 Cross-category shopper filter applied")
        
        # Check for price tier preferences
        if 'premium' in search_text or 'luxury' in search_text or 'high-end' in search_text:
            filters.append("cs.price_tier_preference = 'premium'")
            print(f"   💎 Premium tier filter applied")
        elif 'budget' in search_text or 'affordable' in search_text or 'value' in search_text:
            filters.append("cs.price_tier_preference = 'budget'")
            print(f"   💰 Budget tier filter applied")
        
        return filters

