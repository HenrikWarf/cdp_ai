"""
Segment Service - Orchestrates the entire segmentation pipeline
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from backend.models.intent_interpreter import CampaignIntentInterpreter
from backend.models.causal_engine import CausalSegmentationEngine
from backend.models.query_builder import QueryBuilder
from backend.services.bigquery_service import BigQueryService
from backend.api.schemas import (
    CampaignObjectiveObject,
    SegmentResponse,
    SegmentMetadata,
    CustomerProfile,
    TriggerRecommendation,
    CampaignAnalysisResponse
)
from backend.utils.helpers import generate_segment_id, format_currency
from backend.config import Config


class SegmentService:
    """
    Main service that orchestrates the AI-driven segmentation pipeline:
    1. Interpret campaign objective (LLM)
    2. Calculate uplift scores (Causal Engine)
    3. Build and execute queries (BigQuery)
    4. Return actionable segments
    """
    
    def __init__(self):
        """Initialize the segment service with all components"""
        self.intent_interpreter = CampaignIntentInterpreter()
        self.causal_engine = CausalSegmentationEngine()
        self.query_builder = QueryBuilder()
        self.bigquery_service = BigQueryService()
        
        # Cache for segments
        self.segment_cache: Dict[str, Dict[str, Any]] = {}
    
    def analyze_campaign(self, campaign_objective: str) -> CampaignAnalysisResponse:
        """
        Analyze a campaign objective and return insights
        
        Args:
            campaign_objective: Natural language campaign description
        
        Returns:
            CampaignAnalysisResponse with COO, segment preview, and trigger suggestions
        """
        # Step 1: Interpret the campaign objective
        coo = self.intent_interpreter.interpret(campaign_objective)
        
        print(f"\n🎯 Campaign Objective Object:")
        print(f"   Goal: {coo.campaign_goal}")
        print(f"   Target Behavior: {coo.target_behavior}")
        print(f"   Target Subgroup: {coo.target_subgroup}")
        print(f"   Time Constraint: {coo.time_constraint}")
        print(f"   Proposed Intervention: {coo.proposed_intervention}")
        
        # Step 2: Build query for full segment (no limit for accurate metrics)
        full_segment_query = self.query_builder.build_segment_query(coo, limit=None)
        
        # Step 3: Get ACTUAL full segment data for accurate metrics
        print(f"\n📊 Fetching full segment data...")
        print(f"\n🔍 Query Preview:")
        # Show first 300 chars of query for debugging
        query_preview = full_segment_query[:300].replace('\n', ' ')
        print(f"   {query_preview}...")
        
        full_customer_data = self.bigquery_service.query(full_segment_query)
        print(f"\n✅ Query executed successfully!")
        print(f"   Total customers in segment: {len(full_customer_data)}")
        
        if len(full_customer_data) > 0:
            print(f"   Avg CLV: {full_customer_data['clv_score'].mean():.3f}")
            if 'cart_value' in full_customer_data.columns:
                print(f"   Avg Cart Value: ${full_customer_data['cart_value'].mean():.2f}")
        
        # Step 4: Get trigger recommendations (can use sample or full data)
        # For large segments, we could sample here, but using full data is more accurate
        trigger_suggestions = self.causal_engine.recommend_triggers(
            full_customer_data, coo
        )
        
        # Step 5: Calculate segment preview metadata from FULL segment
        segment_preview = self._calculate_segment_metadata(
            full_customer_data, 
            coo,
            trigger_suggestions[0] if trigger_suggestions else None
        )
        
        # Step 6: Generate explainability data
        explainability = self._generate_explainability(
            coo, full_customer_data, trigger_suggestions
        )
        
        print(f"\n🎯 Creating CampaignAnalysisResponse...")
        print(f"   Segment preview size: {segment_preview.estimated_size}")
        print(f"   Trigger suggestions: {len(trigger_suggestions)}")
        print(f"   AI filters: {len(segment_preview.ai_filters)}")
        
        try:
            response = CampaignAnalysisResponse(
                campaign_objective_object=coo,
                segment_preview=segment_preview,
                trigger_suggestions=trigger_suggestions,
                explainability=explainability
            )
            print(f"   ✅ CampaignAnalysisResponse created successfully")
            return response
        except Exception as e:
            print(f"\n❌ Error creating CampaignAnalysisResponse: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def create_segment(
        self,
        campaign_objective: str,
        override_trigger: Optional[str] = None,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> SegmentResponse:
        """
        Create a complete customer segment for activation
        
        Args:
            campaign_objective: Natural language campaign description
            override_trigger: Optional trigger to override AI recommendation
            additional_filters: Optional additional filters (location, CLV, etc.)
        
        Returns:
            SegmentResponse with full customer list and metadata
        """
        # Step 1: Interpret the campaign objective
        coo = self.intent_interpreter.interpret(campaign_objective)
        
        # Step 2: Get trigger recommendations
        sample_query = self.query_builder.build_segment_query(coo, limit=1000)
        sample_data = self.bigquery_service.query(sample_query)
        
        # Debug: Show what data we got from BigQuery
        print(f"\n📊 BigQuery Data Retrieved:")
        print(f"   Rows: {len(sample_data)}")
        print(f"   Columns: {list(sample_data.columns)}")
        if len(sample_data) > 0:
            print(f"   Sample sensitivity scores:")
            if 'discount_sensitivity_score' in sample_data.columns:
                print(f"     - discount_sensitivity: {sample_data['discount_sensitivity_score'].mean():.3f}")
            if 'free_shipping_sensitivity_score' in sample_data.columns:
                print(f"     - free_shipping_sensitivity: {sample_data['free_shipping_sensitivity_score'].mean():.3f}")
            if 'clv_score' in sample_data.columns:
                print(f"     - clv_score: {sample_data['clv_score'].mean():.3f}")
        
        trigger_suggestions = self.causal_engine.recommend_triggers(sample_data, coo)
        
        # Select trigger
        if override_trigger:
            selected_trigger = override_trigger
        else:
            selected_trigger = trigger_suggestions[0].trigger_name if trigger_suggestions else 'discount'
        
        # Step 3: Build final segment query
        # NEW FLOW: Trigger sensitivity filter is ALWAYS applied (if trigger selected)
        # Manual filters (location, CLV) are applied AFTER in Python
        print(f"\n📋 Building segment query...")
        print(f"   ✓ AI behavior filters: ACTIVE (from campaign objective)")
        print(f"   ✓ Trigger sensitivity filter: ACTIVE ('{selected_trigger}')")
        if additional_filters and len(additional_filters) > 0:
            print(f"   ✓ Manual filters: Will apply after SQL query")
        
        # Always apply trigger sensitivity in SQL
        uplift_scores = {selected_trigger: Config.DEFAULT_UPLIFT_THRESHOLD}
        
        # Step 4: Build segment query
        segment_query = self.query_builder.build_segment_query(
            coo,
            uplift_scores=uplift_scores,
            limit=Config.MAX_SEGMENT_SIZE
        )
        
        # Step 5: Execute query and get customers
        customer_df = self.bigquery_service.query(segment_query)
        print(f"\n📊 Initial segment size from BigQuery: {len(customer_df)}")
        
        # Step 5.5: Apply additional filters if provided
        if additional_filters and len(additional_filters) > 0:
            print(f"\n🔧 Applying additional filters: {additional_filters}")
            initial_size = len(customer_df)
            customer_df = self._apply_filters(customer_df, additional_filters)
            final_size = len(customer_df)
            print(f"   Segment size: {initial_size} → {final_size} customers")
            
            if final_size == 0:
                print(f"   ⚠️  WARNING: All customers filtered out!")
                print(f"   Check if filters are too restrictive or data exists")
        
        # Step 6: Convert to customer profiles
        customer_profiles = self._df_to_customer_profiles(customer_df, coo)
        
        # Step 7: Calculate metadata
        metadata = self._calculate_segment_metadata(
            customer_df, coo, 
            trigger_suggestions[0] if trigger_suggestions else None
        )
        
        # Step 7.5: Generate comprehensive explainability including all filtering steps
        comprehensive_explainability = self._generate_comprehensive_summary(
            coo,
            customer_df,
            trigger_suggestions,
            selected_trigger,
            additional_filters
        )
        
        # Step 8: Generate segment ID and cache
        segment_id = generate_segment_id(campaign_objective)
        
        response = SegmentResponse(
            segment_id=segment_id,
            campaign_objective_ref=campaign_objective,
            query_timestamp=datetime.utcnow(),
            estimated_size=len(customer_profiles),
            criteria_used=segment_query,
            customer_profiles=customer_profiles[:100],  # Limit response size
            metadata=metadata,
            recommended_trigger=trigger_suggestions[0] if trigger_suggestions else None,
            comprehensive_summary=comprehensive_explainability  # Add full journey summary
        )
        
        print(f"\n✅ Segment created successfully!")
        print(f"   Segment ID: {segment_id}")
        print(f"   Total customers: {len(customer_profiles)}")
        print(f"   Customers in response: {len(customer_profiles[:100])}")
        print(f"   Trigger: {selected_trigger}")
        print(f"   Manual filters: {additional_filters}")
        
        # Cache the segment
        self.segment_cache[segment_id] = {
            'response': response,
            'full_customer_list': customer_profiles,
            'query': segment_query,
            'created_at': datetime.utcnow()
        }
        
        return response
    
    def get_segment_customers(
        self,
        segment_id: str,
        limit: Optional[int] = None
    ) -> List[CustomerProfile]:
        """
        Get customer list for a cached segment
        
        Args:
            segment_id: The segment identifier
            limit: Optional limit on number of customers
        
        Returns:
            List of CustomerProfile objects
        """
        if segment_id not in self.segment_cache:
            raise ValueError(f"Segment {segment_id} not found")
        
        customers = self.segment_cache[segment_id]['full_customer_list']
        
        if limit:
            return customers[:limit]
        return customers
    
    def get_segment_metadata(self, segment_id: str) -> SegmentMetadata:
        """
        Get metadata for a cached segment
        
        Args:
            segment_id: The segment identifier
        
        Returns:
            SegmentMetadata object
        """
        if segment_id not in self.segment_cache:
            raise ValueError(f"Segment {segment_id} not found")
        
        return self.segment_cache[segment_id]['response'].metadata
    
    def _apply_filters(self, customer_df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply additional filters to a customer DataFrame
        
        Args:
            customer_df: DataFrame with customer data
            filters: Dictionary of filters to apply
        
        Returns:
            Filtered DataFrame
        """
        filtered_data = customer_df.copy()
        
        # Location filters (case-insensitive for robustness)
        if 'location_country' in filters and filters['location_country']:
            country = filters['location_country']
            filtered_data = filtered_data[
                filtered_data['location_country'].str.lower() == country.lower()
            ]
            print(f"   📍 Country filter ({country}): {len(filtered_data)} customers")
        
        if 'location_city' in filters and filters['location_city']:
            city = filters['location_city']
            filtered_data = filtered_data[
                filtered_data['location_city'].str.lower() == city.lower()
            ]
            print(f"   📍 City filter ({city}): {len(filtered_data)} customers")
        
        # CLV filter
        if 'clv_min' in filters:
            clv_min = float(filters['clv_min'])
            filtered_data = filtered_data[
                filtered_data['clv_score'] >= clv_min
            ]
            print(f"   💰 CLV filter (>= {clv_min:.0%}): {len(filtered_data)} customers")
        
        # Cart value filter
        if 'cart_value_min' in filters and 'cart_value' in filtered_data.columns:
            cart_min = float(filters['cart_value_min'])
            filtered_data = filtered_data[
                filtered_data['cart_value'] >= cart_min
            ]
            print(f"   🛒 Cart value filter (>= ${cart_min:.2f}): {len(filtered_data)} customers")
        
        return filtered_data
    
    def preview_filter_impact(
        self, 
        coo_data: dict, 
        new_filters: dict,
        selected_trigger: Optional[str] = None
    ):
        """
        Preview the impact of additional filters on segment size/quality
        
        Args:
            coo_data: Campaign Objective Object as dict
            new_filters: Additional filters to apply (location, CLV, cart value, etc.)
            selected_trigger: Optional trigger name to apply sensitivity filter
        
        Returns:
            FilterPreviewResponse with before/after metrics
        """
        from backend.api.schemas import CampaignObjectiveObject, FilterPreviewResponse
        
        # Convert dict to COO
        coo = CampaignObjectiveObject(**coo_data)
        
        # Get the base segment (AI-filtered + trigger filter if selected)
        # CRITICAL: If a trigger was selected, apply its sensitivity filter here
        uplift_scores = None
        if selected_trigger:
            uplift_scores = {selected_trigger: Config.DEFAULT_UPLIFT_THRESHOLD}
            print(f"\n🎯 Preview with trigger filter: '{selected_trigger}' (threshold: {Config.DEFAULT_UPLIFT_THRESHOLD})")
        
        base_query = self.query_builder.build_segment_query(
            coo, 
            uplift_scores=uplift_scores,
            limit=None
        )
        base_data = self.bigquery_service.query(base_query)
        starting_size = len(base_data)
        print(f"   Starting size (after trigger filter): {starting_size} customers")
        
        # Apply new filters to the DataFrame using reusable method
        filtered_data = self._apply_filters(base_data, new_filters)
        
        # Track what filters were applied for response
        filters_applied = []
        
        # Location filters
        if 'location_country' in new_filters and new_filters['location_country']:
            filters_applied.append({
                'type': 'location',
                'description': f"Country: {new_filters['location_country']}",
                'impact': len(filtered_data)
            })
        
        if 'location_city' in new_filters and new_filters['location_city']:
            filters_applied.append({
                'type': 'location',
                'description': f"City: {new_filters['location_city']}",
                'impact': len(filtered_data)
            })
        
        # CLV filter
        if 'clv_min' in new_filters:
            clv_min = float(new_filters['clv_min'])
            filters_applied.append({
                'type': 'value',
                'description': f"CLV Score ≥ {clv_min:.0%}",
                'impact': len(filtered_data)
            })
        
        # Cart value filter
        if 'cart_value_min' in new_filters and 'cart_value' in filtered_data.columns:
            cart_min = float(new_filters['cart_value_min'])
            filters_applied.append({
                'type': 'cart_value',
                'description': f"Cart Value ≥ ${cart_min:.2f}",
                'impact': len(filtered_data)
            })
        
        # Calculate final metrics
        final_size = len(filtered_data)
        percentage_retained = (final_size / starting_size * 100) if starting_size > 0 else 0
        
        final_avg_clv = float(filtered_data['clv_score'].mean()) if final_size > 0 else 0.0
        final_avg_cart_value = None
        if 'cart_value' in filtered_data.columns and final_size > 0:
            cart_mean = filtered_data['cart_value'].mean()
            if not pd.isna(cart_mean):
                final_avg_cart_value = float(cart_mean)
        
        # Calculate demographic breakdown for filtered data
        demographic_breakdown = {}
        if 'location_country' in filtered_data.columns and final_size > 0:
            all_countries = filtered_data['location_country'].value_counts().to_dict()
            demographic_breakdown['top_countries'] = {
                str(k): int(v) for k, v in all_countries.items() 
                if not (pd.isna(k) or pd.isna(v))
            }
        
        return FilterPreviewResponse(
            starting_size=starting_size,
            final_size=final_size,
            percentage_retained=round(percentage_retained, 1),
            filters_applied=filters_applied,
            final_avg_clv=round(final_avg_clv, 3),
            final_avg_cart_value=round(final_avg_cart_value, 2) if final_avg_cart_value else None,
            demographic_breakdown=demographic_breakdown
        )
    
    def _extract_ai_filters(self, coo: CampaignObjectiveObject) -> List:
        """Extract AI-applied filters from Campaign Objective Object"""
        try:
            from backend.api.schemas import AIFilter
            
            ai_filters = []
            
            print(f"\n🔍 Extracting AI Filters...")
            print(f"   target_behavior: '{coo.target_behavior}'")
            print(f"   target_subgroup: '{coo.target_subgroup}'")
            print(f"   time_constraint: '{coo.time_constraint}'")
            
            # Behavior filter
            if coo.target_behavior:
                print(f"   ✓ Has target_behavior: {coo.target_behavior}")
                
                if coo.target_behavior == "abandoned_cart":
                    print(f"   ✓ Adding abandoned_cart behavior filter")
                    ai_filters.append(AIFilter(
                        filter_type="behavior",
                        description=f"Target Behavior: Abandoned Cart",
                        sql_condition="ac.status = 'abandoned'",
                        can_modify=False
                    ))
                elif coo.target_behavior == "lapsed_customer":
                    print(f"   ✓ Adding lapsed_customer behavior filter")
                    ai_filters.append(AIFilter(
                        filter_type="behavior",
                        description=f"Target Behavior: Lapsed Customer (high churn risk)",
                        sql_condition="cs.churn_probability_score > 0.6",
                        can_modify=True
                    ))
                elif coo.target_behavior in ["high_engagement", "active_customer"]:
                    print(f"   ✓ Adding engagement behavior filter")
                    ai_filters.append(AIFilter(
                        filter_type="behavior",
                        description=f"Target Behavior: High Engagement",
                        sql_condition="cs.content_engagement_score > 0.7",
                        can_modify=True
                    ))
                else:
                    print(f"   ℹ️  Behavior '{coo.target_behavior}' - no specific filter (using base filters only)")
            
            # Timing filter
            if coo.time_constraint:
                print(f"   ✓ Adding timing filter")
                ai_filters.append(AIFilter(
                    filter_type="timing",
                    description=f"Time Window: {coo.time_constraint.replace('_', ' ').title()}",
                    sql_condition=f"TIMESTAMP(ac.timestamp) > TIMESTAMP(...)",  # Simplified
                    can_modify=True
                ))
            
            # Value filter (CLV for high-value shoppers)
            if coo.target_subgroup and "high_value" in coo.target_subgroup.lower():
                print(f"   ✓ Adding CLV filter (high_value in subgroup)")
                ai_filters.append(AIFilter(
                    filter_type="value",
                    description="Customer Value: High CLV (≥ 0.75, top 25%)",
                    sql_condition="c.clv_score >= 0.75",
                    can_modify=True
                ))
            
            # Cart value filter (ONLY for abandoned cart campaigns)
            if coo.target_behavior == "abandoned_cart":
                print(f"   ✓ Adding cart value filter")
                ai_filters.append(AIFilter(
                    filter_type="cart_value",
                    description="Cart Value: Above average",
                    sql_condition="ac.cart_value > (SELECT AVG(cart_value) FROM abandoned_carts)",
                    can_modify=True
                ))
            
            # Cross-sell campaigns
            elif coo.target_behavior == "cross_sell":
                print(f"   ✓ Adding cross_sell behavior filter")
                ai_filters.append(AIFilter(
                    filter_type="behavior",
                    description=f"Target Behavior: Cross-Sell (recent product purchasers)",
                    sql_condition="EXISTS (SELECT 1 FROM transactions WHERE customer_id = c.customer_id AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))",
                    can_modify=True
                ))
            
            # New customer acquisition
            elif coo.target_behavior in ["new_customer", "acquisition"]:
                print(f"   ✓ Adding new_customer behavior filter")
                ai_filters.append(AIFilter(
                    filter_type="behavior",
                    description=f"Target Behavior: New Customer (acquired in last 7 days)",
                    sql_condition="c.creation_date > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)",
                    can_modify=True
                ))
            
            # Retention campaigns
            elif coo.target_behavior in ["retention", "repeat_purchase"]:
                print(f"   ✓ Adding retention behavior filter")
                ai_filters.append(AIFilter(
                    filter_type="behavior",
                    description=f"Target Behavior: At-Risk Retention (30-90 days since last purchase)",
                    sql_condition="EXISTS (SELECT 1 FROM transactions WHERE customer_id = c.customer_id AND timestamp BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))",
                    can_modify=True
                ))
            
            # Reactivation campaigns
            elif coo.target_behavior in ["reactivation", "dormant"]:
                print(f"   ✓ Adding reactivation behavior filter")
                ai_filters.append(AIFilter(
                    filter_type="behavior",
                    description=f"Target Behavior: Reactivation (high churn risk)",
                    sql_condition="cs.churn_probability_score > 0.6",
                    can_modify=True
                ))
            
            # Additional filters based on campaign goal
            if coo.campaign_goal == "win_back" and coo.target_behavior == "lapsed_customer":
                print(f"   ✓ Adding win-back specific filter (exclusivity seekers)")
                # Win-back campaigns work better with exclusivity-seeking customers
                ai_filters.append(AIFilter(
                    filter_type="preference",
                    description="Customer Preference: Exclusivity Seekers",
                    sql_condition="cs.exclusivity_seeker_flag = true",
                    can_modify=True
                ))
            
            print(f"   📝 Total AI filters extracted: {len(ai_filters)}")
            return ai_filters
        except Exception as e:
            print(f"\n⚠️  Warning: Failed to extract AI filters: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_segment_metadata(
        self,
        customer_df: pd.DataFrame,
        coo: CampaignObjectiveObject,
        top_trigger: Optional[TriggerRecommendation] = None
    ) -> SegmentMetadata:
        """Calculate metadata about the segment"""
        
        print(f"\n📊 Calculating segment metadata...")
        print(f"   Customer DataFrame shape: {customer_df.shape}")
        print(f"   Columns: {list(customer_df.columns)}")
        
        segment_id = generate_segment_id(coo.proposed_intervention)
        estimated_size = len(customer_df)
        
        print(f"   Segment ID: {segment_id}")
        print(f"   Estimated size: {estimated_size}")
        
        # Extract AI-applied filters
        ai_filters = self._extract_ai_filters(coo)
        print(f"   AI Filters extracted: {len(ai_filters)}")
        
        # Calculate average CLV (handle NaN)
        if 'clv_score' in customer_df.columns and len(customer_df) > 0:
            avg_clv = customer_df['clv_score'].mean()
            # Replace NaN with default
            avg_clv = 0.7 if pd.isna(avg_clv) else float(avg_clv)
        else:
            avg_clv = 0.7
        
        # Calculate average cart value if applicable (handle NaN)
        avg_cart_value = None
        if 'cart_value' in customer_df.columns and len(customer_df) > 0:
            cart_mean = customer_df['cart_value'].mean()
            if not pd.isna(cart_mean):
                avg_cart_value = float(cart_mean)
        
        # Get common product categories
        common_categories = []
        if 'cart_items' in customer_df.columns:
            # This would need proper parsing in production
            common_categories = ['Electronics', 'Fashion', 'Home & Garden']
        
        # Demographic breakdown - show ALL countries for accurate totals
        demographic_breakdown = {}
        if 'location_country' in customer_df.columns and len(customer_df) > 0:
            # Get all countries, sorted by count (descending)
            all_countries = customer_df['location_country'].value_counts().to_dict()
            # Convert numpy types to Python types and handle NaN
            demographic_breakdown['top_countries'] = {
                str(k): int(v) for k, v in all_countries.items() 
                if not (pd.isna(k) or pd.isna(v))
            }
        
        # Calculate predicted uplift and ROI
        predicted_uplift = top_trigger.predicted_uplift if top_trigger else 0.15
        predicted_roi = "4-6x" if predicted_uplift > 0.6 else "2-4x"
        
        print(f"   Creating SegmentMetadata with ai_filters: {len(ai_filters)}")
        
        try:
            metadata = SegmentMetadata(
                segment_id=segment_id,
                estimated_size=estimated_size,
                predicted_uplift=predicted_uplift,
                predicted_roi=predicted_roi,
                avg_clv_score=avg_clv,
                avg_cart_value=avg_cart_value,
                common_product_categories=common_categories,
                demographic_breakdown=demographic_breakdown,
                ai_filters=ai_filters
            )
            print(f"   ✅ SegmentMetadata created successfully")
            return metadata
        except Exception as e:
            print(f"\n❌ Error creating SegmentMetadata: {str(e)}")
            # Fallback to metadata without ai_filters
            print(f"   Falling back to metadata without ai_filters")
            return SegmentMetadata(
                segment_id=segment_id,
                estimated_size=estimated_size,
                predicted_uplift=predicted_uplift,
                predicted_roi=predicted_roi,
                avg_clv_score=avg_clv,
                avg_cart_value=avg_cart_value,
                common_product_categories=common_categories,
                demographic_breakdown=demographic_breakdown,
                ai_filters=[]
            )
    
    def _df_to_customer_profiles(
        self,
        df: pd.DataFrame,
        coo: CampaignObjectiveObject
    ) -> List[CustomerProfile]:
        """Convert DataFrame to list of CustomerProfile objects"""
        profiles = []
        
        for _, row in df.iterrows():
            # Handle NaN values properly
            clv_score = row.get('clv_score', 0.5)
            clv_score = 0.5 if pd.isna(clv_score) else float(clv_score)
            
            location_city = row.get('location_city') if 'location_city' in row else None
            if location_city is not None and pd.isna(location_city):
                location_city = None
            
            profile = CustomerProfile(
                customer_id=str(row.get('customer_id', '')),
                email=str(row.get('email_address', '')),
                first_name=str(row.get('first_name', 'Valued Customer')),
                clv_score=clv_score,
                location_city=str(location_city) if location_city is not None else None
            )
            
            # Add abandoned cart data if available
            if 'abandoned_cart_id' in row and not pd.isna(row['abandoned_cart_id']):
                profile.abandoned_cart_id = str(row['abandoned_cart_id'])
                
                cart_value = row.get('cart_value', 0)
                profile.cart_value = 0.0 if pd.isna(cart_value) else float(cart_value)
                
                # Parse cart items if available
                if 'cart_items' in row and row['cart_items'] and not pd.isna(row['cart_items']):
                    # In production, this would be properly parsed JSON
                    profile.cart_items = ['Product A', 'Product B']
            
            profiles.append(profile)
        
        return profiles
    
    def _generate_explainability(
        self,
        coo: CampaignObjectiveObject,
        customer_data: pd.DataFrame,
        trigger_suggestions: List[TriggerRecommendation]
    ) -> Dict[str, Any]:
        """Generate explainability information for the segment"""
        
        # Get feature importance - now calculated from REAL data
        feature_importance = self.causal_engine.get_feature_importance(
            coo.proposed_intervention,
            customer_data  # Pass actual customer data
        )
        
        # Generate explanation text
        top_trigger = trigger_suggestions[0] if trigger_suggestions else None
        
        explanation = {
            'why_this_segment': self._generate_segment_explanation(coo, customer_data),
            'key_factors': self._format_key_factors(feature_importance),
            'recommended_trigger': top_trigger.trigger_name if top_trigger else None,
            'trigger_rationale': top_trigger.rationale if top_trigger else None,
            'sample_size': len(customer_data),
            'confidence_level': 'high' if len(customer_data) > 500 else 'moderate'
        }
        
        return explanation
    
    def _generate_segment_explanation(
        self,
        coo: CampaignObjectiveObject,
        customer_data: pd.DataFrame
    ) -> str:
        """Generate human-readable explanation for why this segment was chosen"""
        
        avg_clv = customer_data['clv_score'].mean() if 'clv_score' in customer_data.columns else 0.7
        
        explanation = (
            f"This segment was selected based on your campaign goal to {coo.campaign_goal} "
            f"for customers exhibiting {coo.target_behavior} behavior. "
        )
        
        if coo.target_subgroup:
            explanation += (
                f"We focused on {coo.target_subgroup} (average CLV score: {avg_clv:.2f}). "
            )
        
        if coo.time_constraint:
            explanation += (
                f"The segment includes only customers within the {coo.time_constraint} timeframe. "
            )
        
        explanation += (
            f"Based on historical campaign data, the {coo.proposed_intervention} intervention "
            f"is predicted to have the highest impact on this audience."
        )
        
        return explanation
    
    def _format_key_factors(self, feature_importance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Format feature importance for frontend display"""
        factors = []
        
        for feature, importance in feature_importance.items():
            factors.append({
                'feature': feature.replace('_', ' ').title(),
                'importance': importance,
                'description': self._get_feature_description(feature)
            })
        
        return factors
    
    def _generate_comprehensive_summary(
        self,
        coo: CampaignObjectiveObject,
        customer_data: pd.DataFrame,
        trigger_suggestions: List[TriggerRecommendation],
        selected_trigger: Optional[str],
        additional_filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary of the entire segment creation journey
        Including: Campaign goal → AI filters → Trigger selection → Manual filters → Final segment
        """
        
        # Get basic stats
        avg_clv = customer_data['clv_score'].mean() if 'clv_score' in customer_data.columns and len(customer_data) > 0 else 0.7
        avg_clv = float(avg_clv) if not pd.isna(avg_clv) else 0.7
        
        # Build filtering journey steps
        filtering_steps = []
        
        # Step 1: Campaign Objective
        filtering_steps.append({
            'step': 'Campaign Objective',
            'description': f"Goal: {coo.campaign_goal.replace('_', ' ').title()} campaign targeting {coo.target_behavior.replace('_', ' ')} behavior"
        })
        
        # Step 2: AI Behavioral Filters
        ai_filter_desc = []
        if coo.target_behavior:
            behavior_labels = {
                'abandoned_cart': 'Abandoned cart in last 7 days',
                'lapsed_customer': 'High churn risk customers (churn score > 60%)',
                'high_engagement': 'High engagement customers (engagement score > 70%)',
                'cross_sell': 'Recent product purchasers (last 30 days)',
                'new_customer': 'New customers (acquired in last 7 days)',
                'retention': 'At-risk retention (30-90 days since last purchase)',
                'reactivation': 'Dormant customers (high churn probability)'
            }
            ai_filter_desc.append(behavior_labels.get(coo.target_behavior, f'{coo.target_behavior} behavior'))
        
        if coo.target_subgroup and "high_value" in coo.target_subgroup.lower():
            ai_filter_desc.append('High CLV customers (top 25%, score ≥ 75%)')
        
        if coo.target_behavior == "abandoned_cart":
            ai_filter_desc.append('Above-average cart value')
        
        if ai_filter_desc:
            filtering_steps.append({
                'step': 'AI Behavioral Filters',
                'description': ' • ' + '\n • '.join(ai_filter_desc)
            })
        
        # Step 3: Trigger Selection
        if selected_trigger:
            trigger_obj = next((t for t in trigger_suggestions if t.trigger_name == selected_trigger), None)
            trigger_display = selected_trigger.replace('_', ' ').title()
            if trigger_obj:
                filtering_steps.append({
                    'step': 'Trigger Selection',
                    'description': f"Selected: {trigger_display}\nSensitivity threshold: 65%\nPredicted uplift: {int(trigger_obj.predicted_uplift * 100)}%"
                })
            else:
                filtering_steps.append({
                    'step': 'Trigger Selection',
                    'description': f"Selected: {trigger_display}\nSensitivity threshold: 65%"
                })
        
        # Step 4: Manual Refinements
        if additional_filters and len(additional_filters) > 0:
            manual_filter_desc = []
            if 'location_country' in additional_filters:
                manual_filter_desc.append(f"Country: {additional_filters['location_country']}")
            if 'location_city' in additional_filters:
                manual_filter_desc.append(f"City: {additional_filters['location_city']}")
            if 'clv_min' in additional_filters:
                clv_min_pct = int(float(additional_filters['clv_min']) * 100)
                manual_filter_desc.append(f"Minimum CLV: {clv_min_pct}%")
            if 'cart_value_min' in additional_filters:
                cart_min = float(additional_filters['cart_value_min'])
                manual_filter_desc.append(f"Minimum cart value: ${cart_min:.2f}")
            
            if manual_filter_desc:
                filtering_steps.append({
                    'step': 'Manual Refinements',
                    'description': ' • ' + '\n • '.join(manual_filter_desc)
                })
        
        # Final segment characteristics
        final_characteristics = {
            'total_customers': len(customer_data),
            'avg_clv_score': round(avg_clv, 3),
            'primary_location': None,
            'filtering_steps': filtering_steps
        }
        
        # Get primary location if available
        if 'location_country' in customer_data.columns and len(customer_data) > 0:
            top_country = customer_data['location_country'].mode()
            if len(top_country) > 0 and not pd.isna(top_country.iloc[0]):
                final_characteristics['primary_location'] = str(top_country.iloc[0])
        
        # Generate summary text
        summary_text = f"This segment of {len(customer_data):,} customers was created through a {len(filtering_steps)}-step refinement process:\n\n"
        
        for i, step in enumerate(filtering_steps, 1):
            summary_text += f"{i}. **{step['step']}**: {step['description']}\n"
        
        summary_text += f"\n**Final Result**: {len(customer_data):,} highly-targeted customers with an average CLV score of {int(avg_clv * 100)}%, optimized for maximum campaign impact."
        
        return {
            'summary_text': summary_text,
            'filtering_steps': filtering_steps,
            'final_characteristics': final_characteristics,
            'confidence_level': 'high' if len(customer_data) > 500 else 'moderate'
        }
    
    def _get_feature_description(self, feature: str) -> str:
        """Get human-readable description of a feature"""
        descriptions = {
            'clv_score': 'Customer lifetime value prediction',
            'discount_sensitivity_score': 'Likelihood to respond to discounts',
            'cart_value': 'Value of items in abandoned cart',
            'purchase_frequency': 'How often the customer purchases',
            'free_shipping_sensitivity_score': 'Responsiveness to free shipping offers',
            'time_since_last_purchase': 'Recency of last transaction',
            'avg_order_value': 'Average amount spent per order',
            'churn_probability_score': 'Risk of customer leaving'
        }
        
        return descriptions.get(feature, feature.replace('_', ' ').capitalize())

