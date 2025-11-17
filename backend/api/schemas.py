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
    proposed_intervention: List[str]  # List of potential intervention types for evaluation
    underlying_assumptions: List[str] = []
    demographic_filters: Optional[Dict[str, Any]] = None  # Age, gender, income, location filters
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_goal": "conversion",
                "target_behavior": "abandoned_cart",
                "target_subgroup": "high_value_shopper",
                "metric_target": {"type": "conversion_rate_increase", "value": 0.20},
                "time_constraint": "48_hours_post_abandonment",
                "proposed_intervention": ["discount", "free_shipping"],
                "underlying_assumptions": ["price_sensitive", "prior_engagement_with_products"],
                "demographic_filters": {
                    "age_min": 25,
                    "age_max": 35,
                    "gender": "Female",
                    "income_level": "high",
                    "location_country": "United States",
                    "location_city": "New York"
                }
            }
        }


class TriggerRecommendation(BaseModel):
    """Individual trigger recommendation with uplift predictions"""
    trigger_type: str
    trigger_name: str
    confidence_score: float  # Statistical confidence in the prediction (0-1), based on consistency across customers
    predicted_uplift: float  # Expected conversion rate increase (0-1), e.g., 0.72 = 72% uplift
    description: str
    rationale: str


class CLVInterpretation(BaseModel):
    """Business-friendly interpretation of CLV score"""
    tier: str  # 'premium', 'high', 'medium', 'low'
    tier_label: str  # 'Premium', 'Above Average', 'Average', 'Below Average'
    score_percentage: str  # e.g., "72%"
    score_raw: float  # Raw score 0-1
    vs_baseline: float  # Percentage difference from baseline
    vs_baseline_label: str  # 'Above Average', 'At Baseline', 'Below Average'
    vs_baseline_formatted: str  # e.g., "+1.4%"
    percentile: str  # e.g., "60-80th"
    description: Optional[str] = None  # Detailed description
    segment_summary: Optional[str] = None  # For segment-level interpretation
    actionable_insight: Optional[str] = None  # Business recommendation


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
    clv_interpretation: Optional[CLVInterpretation] = None  # Business-friendly CLV interpretation
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
    # Product affinity data
    favorite_category: Optional[str] = None
    secondary_category: Optional[str] = None
    price_tier_preference: Optional[str] = None


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
    comprehensive_summary: Optional[Dict[str, Any]] = None  # Full journey summary


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
    clv_interpretation: Optional[CLVInterpretation] = None  # CLV interpretation for preview
    final_avg_cart_value: Optional[float] = None
    percentage_retained: float
    demographic_breakdown: Optional[Dict[str, Any]] = None


class CampaignAnalysisResponse(BaseModel):
    """Response for campaign analysis"""
    campaign_objective_object: CampaignObjectiveObject
    segment_preview: SegmentMetadata
    trigger_suggestions: List[TriggerRecommendation]
    recommended_trigger: TriggerRecommendation  # Auto-selected top trigger
    explainability: Dict[str, Any]


class SegmentCreateRequest(BaseModel):
    """Request to create a new segment"""
    campaign_objective: Optional[str] = None  # For backwards compatibility
    campaign_objective_object: Optional[Dict[str, Any]] = None  # NEW: Accept pre-analyzed COO
    override_trigger: Optional[str] = None
    additional_filters: Optional[Dict[str, Any]] = None
    
    @model_validator(mode='after')
    def validate_campaign_input(self):
        """Ensure either campaign_objective or campaign_objective_object is provided"""
        if not self.campaign_objective and not self.campaign_objective_object:
            raise ValueError("Either campaign_objective or campaign_objective_object must be provided")
        return self


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

