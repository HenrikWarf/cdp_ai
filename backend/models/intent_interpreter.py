"""
Campaign Intent Interpreter using Google Gemini
Parses natural language campaign objectives into structured Campaign Objective Objects (COO)
"""
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from typing import Dict, Any
from backend.config import Config
from backend.api.schemas import CampaignObjectiveObject, MetricTarget


class CampaignIntentInterpreter:
    """
    Gemini-driven campaign intent interpreter that converts natural language
    campaign objectives into structured, machine-readable objects
    """
    
    def __init__(self):
        """Initialize the interpreter with Gemini"""
        # Initialize Vertex AI
        vertexai.init(
            project=Config.GOOGLE_CLOUD_PROJECT,
            location=Config.GOOGLE_CLOUD_REGION
        )
        
        # Initialize Gemini model
        self.model = GenerativeModel(Config.GEMINI_MODEL)
        
        # Configure generation parameters
        self.generation_config = GenerationConfig(
            temperature=Config.GEMINI_TEMPERATURE,
            max_output_tokens=Config.GEMINI_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json"
        )
    
    def interpret(self, campaign_objective: str) -> CampaignObjectiveObject:
        """
        Interpret a natural language campaign objective using Gemini
        
        Args:
            campaign_objective: Natural language campaign description
        
        Returns:
            CampaignObjectiveObject with structured campaign data
        """
        full_prompt = self._build_full_prompt(campaign_objective)
        
        try:
            # Generate response with Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            # Extract JSON from response
            raw_content = response.text
            print(f"\n🤖 Gemini Response:")
            print(f"   Raw response: {raw_content[:300]}...")  # First 300 chars
            
            # Clean the response - remove markdown code blocks if present
            content = raw_content.strip()
            
            # Remove markdown code blocks
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            elif content.startswith("```"):
                content = content[3:]  # Remove ```
            
            if content.endswith("```"):
                content = content[:-3]  # Remove closing ```
            
            content = content.strip()
            
            # Try to fix common JSON issues
            # Remove trailing commas before } or ]
            import re
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            # Remove comments (// or /* */)
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            print(f"   Cleaned JSON: {content[:200]}...")
            
            try:
                parsed = json.loads(content)
                print(f"   ✅ Parsed successfully")
                print(f"   Campaign Goal: {parsed.get('campaign_goal')}")
                print(f"   Target Behavior: {parsed.get('target_behavior')}")
                print(f"   Proposed Intervention: {parsed.get('proposed_intervention')}")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parse error: {str(e)}")
                print(f"   Full content:\n{content}")
                raise
            
            # Convert to Pydantic model
            coo = self._parse_to_coo(parsed)
            return coo
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Decode Error: {str(e)}")
            print(f"   Response content: {content}")
            raise RuntimeError(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            raise RuntimeError(f"Failed to interpret campaign objective: {str(e)}")
    
    def _build_full_prompt(self, campaign_objective: str) -> str:
        """Build the complete prompt for Gemini"""
        return f"""You are an AI marketing campaign analyst specialized in interpreting marketing objectives.
Your task is to analyze natural language campaign descriptions and extract structured information.

You must identify:
1. campaign_goal: The primary goal (e.g., conversion, retention, acquisition, upsell, cross_sell, win_back, reactivation)
2. target_behavior: The specific customer behavior targeted. Use EXACTLY one of these:
   - abandoned_cart (for cart recovery)
   - lapsed_customer (for win-back, high churn risk)
   - high_engagement (for active users)
   - cross_sell (for product recommendations to recent buyers)
   - new_customer (for onboarding, recent signups)
   - retention (for customers at risk of not returning)
   - reactivation (for dormant/inactive customers)
3. target_subgroup: The customer segment (e.g., high_value_shopper, new_customer, loyal_customer)
4. metric_target: The success metric with NUMERIC value as a decimal (e.g., 0.20 for 20% increase)
5. time_constraint: Timeframe for the campaign (e.g., 48_hours_post_abandonment, 7_days, 30_days)
6. proposed_intervention: The trigger/offer type (discount, free_shipping, scarcity, exclusivity, social_proof, content, gift_with_purchase, cashback, bundling)
7. underlying_assumptions: Marketing psychology assumptions (e.g., price_sensitive, urgency_responsive, status_seeking)

Campaign Objective to analyze: "{campaign_objective}"

OUTPUT FORMAT - CRITICAL INSTRUCTIONS:
- Return ONLY the JSON object below
- NO markdown formatting (no ```json or ``` blocks)
- NO comments in the JSON
- NO trailing commas
- Use double quotes for all strings
- Ensure all brackets and braces are properly closed

{{
  "campaign_goal": "<goal>",
  "target_behavior": "<behavior>",
  "target_subgroup": "<subgroup>",
  "metric_target": {{
    "type": "<metric_type>",
    "value": 0.20
  }},
  "time_constraint": "<time_constraint>",
  "proposed_intervention": "<intervention_type>",
  "underlying_assumptions": ["<assumption1>", "<assumption2>"]
}}

IMPORTANT: 
- metric_target.value MUST be a numeric decimal (0.20 for 20%, 0.15 for 15%, etc.)
- target_behavior should use underscore_case from the list above (abandoned_cart, lapsed_customer, high_engagement, cross_sell, new_customer, retention, reactivation)
- All field names must match exactly as shown
- Return ONLY the JSON - nothing before or after it

Ensure all values are specific and actionable. Use standardized terminology."""
    
    def _parse_to_coo(self, parsed_data: Dict[str, Any]) -> CampaignObjectiveObject:
        """
        Convert parsed LLM response to CampaignObjectiveObject
        
        Args:
            parsed_data: Dictionary from LLM response
        
        Returns:
            CampaignObjectiveObject instance
        """
        metric_data = parsed_data.get('metric_target', {})
        
        # Handle metric value safely - convert to float, handle errors
        raw_value = metric_data.get('value', 0.1)
        
        # Try to convert to float, handle non-numeric strings
        try:
            if raw_value is None:
                metric_value = 0.1
            elif isinstance(raw_value, (int, float)):
                metric_value = float(raw_value)
            elif isinstance(raw_value, str):
                # Try to parse string to float
                # Remove common non-numeric characters
                cleaned = raw_value.strip().lower()
                
                # Handle percentage strings like "20%" or "20 percent"
                if '%' in cleaned or 'percent' in cleaned:
                    cleaned = cleaned.replace('%', '').replace('percent', '').strip()
                    metric_value = float(cleaned) / 100  # Convert to decimal
                else:
                    # Try direct conversion
                    metric_value = float(cleaned)
            else:
                metric_value = 0.1
        except (ValueError, TypeError) as e:
            print(f"\n⚠️  Warning: Could not parse metric value '{raw_value}': {str(e)}")
            print(f"   Using default value: 0.1")
            metric_value = 0.1
        
        metric_target = MetricTarget(
            type=metric_data.get('type', 'conversion_rate_increase'),
            value=metric_value
        )
        
        return CampaignObjectiveObject(
            campaign_goal=parsed_data.get('campaign_goal', 'conversion'),
            target_behavior=parsed_data.get('target_behavior', 'general'),
            target_subgroup=parsed_data.get('target_subgroup'),
            metric_target=metric_target,
            time_constraint=parsed_data.get('time_constraint'),
            proposed_intervention=parsed_data.get('proposed_intervention', 'discount'),
            underlying_assumptions=parsed_data.get('underlying_assumptions', [])
        )
    
    def classify_trigger_type(self, intervention: str) -> str:
        """
        Classify the intervention into a trigger category
        
        Args:
            intervention: The proposed intervention
        
        Returns:
            Trigger category (value_driven, psychological, informational)
        """
        value_driven = ['discount', 'free_shipping', 'cashback', 'gift_with_purchase', 
                        'bundling', 'free_trial']
        psychological = ['scarcity', 'urgency', 'social_proof', 'exclusivity', 
                        'reciprocity', 'fomo']
        informational = ['content', 'storytelling', 'personalization', 
                        'educational', 'reviews']
        
        intervention_lower = intervention.lower().replace('_', ' ')
        
        if any(trigger in intervention_lower for trigger in value_driven):
            return 'value_driven'
        elif any(trigger in intervention_lower for trigger in psychological):
            return 'psychological'
        elif any(trigger in intervention_lower for trigger in informational):
            return 'informational'
        else:
            return 'value_driven'  # Default

