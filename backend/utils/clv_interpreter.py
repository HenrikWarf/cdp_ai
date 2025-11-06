"""
CLV Score Interpretation Utility

Converts raw CLV scores (0-1) into business-friendly interpretations
with contextual information for marketers and business users.
"""
from typing import Dict, Any


# Global baseline from data generation (beta(5,2) distribution)
BASELINE_CLV_SCORE = 0.71


def interpret_clv_score(
    score: float, 
    baseline: float = BASELINE_CLV_SCORE,
    include_description: bool = True
) -> Dict[str, Any]:
    """
    Interpret a CLV score and provide business context.
    
    Args:
        score: CLV score (0-1 scale)
        baseline: Baseline CLV score for comparison (default: 0.71)
        include_description: Whether to include detailed description
    
    Returns:
        Dictionary with interpretation details:
        - tier: Value tier classification
        - tier_label: Short tier label (e.g., "High Value")
        - score_percentage: Score as percentage string
        - vs_baseline: Difference from baseline as percentage
        - vs_baseline_label: Label for comparison (e.g., "Above Average", "Below Average")
        - percentile: Estimated percentile ranking
        - description: Detailed business description (if include_description=True)
    """
    
    # Ensure score is valid
    score = max(0.0, min(1.0, score))
    
    # Determine value tier
    if score >= 0.80:
        tier = "premium"
        tier_label = "Premium"
        description = "Exceptional lifetime value - these are your most valuable customers worth premium investment"
        percentile = "Top 20%"
    elif score >= 0.60:
        tier = "high"
        tier_label = "Above Average"
        description = "Strong lifetime value - solid customers worth investing in with targeted campaigns"
        percentile = "60-80th"
    elif score >= 0.40:
        tier = "medium"
        tier_label = "Average"
        description = "Typical lifetime value - standard customer profile requiring balanced approach"
        percentile = "40-60th"
    else:
        tier = "low"
        tier_label = "Below Average"
        description = "Lower lifetime value - requires cost-efficient marketing strategies"
        percentile = "Bottom 40%"
    
    # Calculate difference from baseline
    delta_points = score - baseline
    delta_percent = (delta_points / baseline) * 100 if baseline > 0 else 0
    
    # Determine comparison label
    if abs(delta_percent) < 2:
        vs_baseline_label = "At Baseline"
    elif delta_percent > 0:
        vs_baseline_label = "Above Average"
    else:
        vs_baseline_label = "Below Average"
    
    result = {
        "tier": tier,
        "tier_label": tier_label,
        "score_percentage": f"{score * 100:.0f}%",
        "score_raw": round(score, 3),
        "vs_baseline": round(delta_percent, 1),
        "vs_baseline_label": vs_baseline_label,
        "vs_baseline_formatted": f"{delta_percent:+.1f}%",
        "percentile": percentile
    }
    
    if include_description:
        result["description"] = description
    
    return result


def interpret_segment_clv(
    avg_clv: float,
    segment_size: int,
    baseline: float = BASELINE_CLV_SCORE
) -> Dict[str, Any]:
    """
    Interpret CLV for an entire customer segment.
    
    Args:
        avg_clv: Average CLV score for the segment
        segment_size: Number of customers in segment
        baseline: Baseline CLV score for comparison
    
    Returns:
        Dictionary with segment-level interpretation
    """
    interpretation = interpret_clv_score(avg_clv, baseline, include_description=True)
    
    # Add segment-specific context
    interpretation["segment_size"] = segment_size
    interpretation["segment_summary"] = (
        f"This segment of {segment_size:,} customers has {interpretation['tier_label'].lower()} "
        f"lifetime value with an average CLV score of {interpretation['score_percentage']}"
    )
    
    # Add actionable insight
    if interpretation["tier"] == "premium":
        interpretation["actionable_insight"] = (
            "Prioritize this segment for premium experiences, personalized offers, and retention programs."
        )
    elif interpretation["tier"] == "high":
        interpretation["actionable_insight"] = (
            "Invest in growth campaigns and cross-sell opportunities to maximize value."
        )
    elif interpretation["tier"] == "medium":
        interpretation["actionable_insight"] = (
            "Balance cost-efficiency with engagement to maintain relationship and identify upsell potential."
        )
    else:
        interpretation["actionable_insight"] = (
            "Focus on cost-effective channels and automated campaigns to optimize ROI."
        )
    
    return interpretation


def get_clv_tier_distribution(clv_scores: list) -> Dict[str, Any]:
    """
    Analyze distribution of CLV scores across tiers.
    
    Args:
        clv_scores: List of CLV scores
    
    Returns:
        Dictionary with tier distribution breakdown
    """
    if not clv_scores:
        return {
            "premium": {"count": 0, "percentage": 0},
            "high": {"count": 0, "percentage": 0},
            "medium": {"count": 0, "percentage": 0},
            "low": {"count": 0, "percentage": 0}
        }
    
    total = len(clv_scores)
    premium = sum(1 for s in clv_scores if s >= 0.80)
    high = sum(1 for s in clv_scores if 0.60 <= s < 0.80)
    medium = sum(1 for s in clv_scores if 0.40 <= s < 0.60)
    low = sum(1 for s in clv_scores if s < 0.40)
    
    return {
        "premium": {
            "count": premium,
            "percentage": round((premium / total) * 100, 1),
            "label": "Premium (80-100%)"
        },
        "high": {
            "count": high,
            "percentage": round((high / total) * 100, 1),
            "label": "Above Average (60-80%)"
        },
        "medium": {
            "count": medium,
            "percentage": round((medium / total) * 100, 1),
            "label": "Average (40-60%)"
        },
        "low": {
            "count": low,
            "percentage": round((low / total) * 100, 1),
            "label": "Below Average (<40%)"
        }
    }




