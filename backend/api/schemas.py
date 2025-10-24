"""
Pydantic schemas for request/response validation
"""
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


class CampaignObjectiveRequest(BaseModel):
    """Request schema for campaign objective input"""
    objective: str = Field(..., description="Natural language campaign objective")
    
    class Config:
        json_schema_extra = {
            "example": {
                "objective": "Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers"
            }
        }


class MetricTarget(BaseModel):
    """Metric target specification"""
    type: str = Field(..., description="Type of metric (e.g., conversion_rate_increase)")
    value: float = Field(..., description="Target value (will be parsed from string if needed)")
    
    @field_validator('value', mode='before')
    @classmethod
    def parse_value(cls, v):
        """Parse value to float, handling non-numeric strings gracefully"""
        if v is None:
            return 0.1
        
        if isinstance(v, (int, float)):
            return float(v)
        
        if isinstance(v, str):
            try:
                # Try to parse percentage strings
                cleaned = v.strip().lower()
                if '%' in cleaned or 'percent' in cleaned:
                    cleaned = cleaned.replace('%', '').replace('percent', '').strip()
                    return float(cleaned) / 100
                else:
                    # Try direct conversion
                    return float(cleaned)
            except (ValueError, TypeError):
                # Fallback to default
                print(f"⚠️  Warning: Could not parse metric value '{v}', using 0.1")
                return 0.1
        
        return 0.1


class CampaignObjectiveObject(BaseModel):
    """Structured campaign objective (COO)"""
    campaign_goal: str
    target_behavior: str
    target_subgroup: Optional[str] = None
    metric_target: MetricTarget
    time_constraint: Optional[str] = None
    proposed_intervention: str
    underlying_assumptions: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_goal": "conversion",
                "target_behavior": "abandoned_cart",
                "target_subgroup": "high_value_shopper",
                "metric_target": {"type": "conversion_rate_increase", "value": 0.20},
                "time_constraint": "48_hours_post_abandonment",
                "proposed_intervention": "personalized_discount_offer",
                "underlying_assumptions": ["price_sensitive", "prior_engagement_with_products"]
            }
        }


class TriggerRecommendation(BaseModel):
    """Individual trigger recommendation"""
    trigger_type: str
    trigger_name: str
    confidence_score: float
    predicted_uplift: float
    description: str
    rationale: str


class AIFilter(BaseModel):
    """Represents a filter applied by AI from campaign objective"""
    filter_type: str  # 'behavior', 'timing', 'value', 'cart_value'
    description: str  # Human-readable description
    sql_condition: str  # The actual SQL WHERE clause
    can_modify: bool = True  # Whether user can tighten/loosen


class SegmentMetadata(BaseModel):
    """Metadata about a customer segment"""
    segment_id: str
    estimated_size: int
    predicted_uplift: float
    predicted_roi: str
    avg_clv_score: float
    avg_cart_value: Optional[float] = None
    common_product_categories: List[str] = []
    demographic_breakdown: Dict[str, Any] = {}
    ai_filters: List[AIFilter] = []  # NEW: Track AI-applied filters


class CustomerProfile(BaseModel):
    """Individual customer profile in segment"""
    customer_id: str
    email: str
    first_name: str
    clv_score: float
    location_city: Optional[str] = None
    abandoned_cart_id: Optional[str] = None
    cart_value: Optional[float] = None
    cart_items: Optional[List[str]] = None


class SegmentResponse(BaseModel):
    """Full segment response"""
    segment_id: str
    campaign_objective_ref: str
    query_timestamp: datetime
    estimated_size: int
    criteria_used: str
    customer_profiles: List[CustomerProfile]
    metadata: SegmentMetadata
    recommended_trigger: Optional[TriggerRecommendation] = None


class FilterRefinementRequest(BaseModel):
    """Request to refine segment with additional filters"""
    campaign_objective_object: CampaignObjectiveObject
    ai_filter_modifications: Dict[str, Any] = {}  # Tighten/loosen AI filters
    new_filters: Dict[str, Any] = {}  # Add new filters (location, etc.)


class FilterPreviewResponse(BaseModel):
    """Preview of filter impact"""
    starting_size: int
    final_size: int
    filters_applied: List[Dict[str, Any]]
    final_avg_clv: float
    final_avg_cart_value: Optional[float] = None
    percentage_retained: float
    demographic_breakdown: Optional[Dict[str, Any]] = None


class CampaignAnalysisResponse(BaseModel):
    """Response for campaign analysis"""
    campaign_objective_object: CampaignObjectiveObject
    segment_preview: SegmentMetadata
    trigger_suggestions: List[TriggerRecommendation]
    explainability: Dict[str, Any]


class SegmentCreateRequest(BaseModel):
    """Request to create a new segment"""
    campaign_objective: str
    override_trigger: Optional[str] = None
    additional_filters: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

