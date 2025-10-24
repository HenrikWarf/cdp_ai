"""
API routes for AetherSegment AI
"""
from flask import Blueprint, request, jsonify
from typing import Optional
import traceback

from backend.services.segment_service import SegmentService
from backend.api.schemas import (
    CampaignObjectiveRequest,
    SegmentCreateRequest,
    ErrorResponse
)

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize service
segment_service = SegmentService()


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AetherSegment AI',
        'version': '1.0.0'
    })


@api.route('/campaigns/analyze', methods=['POST'])
def analyze_campaign():
    """
    Analyze a campaign objective and return structured insights
    
    Request Body:
        {
            "objective": "Natural language campaign description"
        }
    
    Returns:
        CampaignAnalysisResponse with COO, segment preview, and trigger suggestions
    """
    try:
        data = request.get_json()
        
        if not data or 'objective' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required field: objective'
            }), 400
        
        # Validate request
        campaign_request = CampaignObjectiveRequest(**data)
        
        # Analyze campaign
        result = segment_service.analyze_campaign(campaign_request.objective)
        
        # Convert to dict for JSON response
        print(f"\n📤 Preparing JSON response...")
        response_dict = result.model_dump()
        print(f"   Response keys: {list(response_dict.keys())}")
        print(f"   Segment preview size in response: {response_dict.get('segment_preview', {}).get('estimated_size', 'N/A')}")
        print(f"   AI filters in response: {len(response_dict.get('segment_preview', {}).get('ai_filters', []))}")
        
        return jsonify(response_dict), 200
        
    except Exception as e:
        print(f"Error in analyze_campaign: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.route('/segments/create', methods=['POST'])
def create_segment():
    """
    Create a complete customer segment for activation
    
    Request Body:
        {
            "campaign_objective": "Natural language campaign description",
            "override_trigger": "optional trigger name"
        }
    
    Returns:
        SegmentResponse with customer list and metadata
    """
    try:
        data = request.get_json()
        
        if not data or 'campaign_objective' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required field: campaign_objective'
            }), 400
        
        # Validate request
        segment_request = SegmentCreateRequest(**data)
        
        # Create segment
        result = segment_service.create_segment(
            segment_request.campaign_objective,
            segment_request.override_trigger,
            segment_request.additional_filters
        )
        
        # Convert to dict for JSON response
        return jsonify(result.model_dump()), 200
        
    except Exception as e:
        print(f"Error in create_segment: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.route('/segments/<segment_id>/customers', methods=['GET'])
def get_segment_customers(segment_id: str):
    """
    Get the customer list for a specific segment
    
    Query Parameters:
        limit: Optional limit on number of customers to return
    
    Returns:
        List of CustomerProfile objects
    """
    try:
        # Get optional limit parameter
        limit = request.args.get('limit', type=int)
        
        # Get customers
        customers = segment_service.get_segment_customers(segment_id, limit)
        
        # Convert to dict list
        customer_dicts = [c.model_dump() for c in customers]
        
        return jsonify({
            'segment_id': segment_id,
            'count': len(customer_dicts),
            'customers': customer_dicts
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Not Found',
            'message': str(e)
        }), 404
    except Exception as e:
        print(f"Error in get_segment_customers: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.route('/segments/<segment_id>/metadata', methods=['GET'])
def get_segment_metadata(segment_id: str):
    """
    Get metadata for a specific segment
    
    Returns:
        SegmentMetadata object
    """
    try:
        # Get metadata
        metadata = segment_service.get_segment_metadata(segment_id)
        
        return jsonify(metadata.model_dump()), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Not Found',
            'message': str(e)
        }), 404
    except Exception as e:
        print(f"Error in get_segment_metadata: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.route('/triggers/suggestions', methods=['POST'])
def get_trigger_suggestions():
    """
    Get trigger recommendations for a campaign objective
    
    Request Body:
        {
            "objective": "Natural language campaign description"
        }
    
    Returns:
        List of TriggerRecommendation objects
    """
    try:
        data = request.get_json()
        
        if not data or 'objective' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required field: objective'
            }), 400
        
        # Analyze campaign to get suggestions
        result = segment_service.analyze_campaign(data['objective'])
        
        # Extract trigger suggestions
        suggestions = [t.model_dump() for t in result.trigger_suggestions]
        
        return jsonify({
            'triggers': suggestions
        }), 200
        
    except Exception as e:
        print(f"Error in get_trigger_suggestions: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.route('/segments/preview-filters', methods=['POST'])
def preview_filter_impact():
    """
    Preview the impact of filter refinements on segment size/quality
    
    Request Body:
        {
            "campaign_objective_object": { ... },
            "new_filters": {
                "location_country": "United States",
                "location_city": "New York",
                "clv_min": 0.8,
                "cart_value_min": 100.0
            },
            "selected_trigger": "discount" (optional)
        }
    
    Returns:
        {
            "starting_size": 5000,
            "final_size": 2300,
            "percentage_retained": 46.0,
            "filters_applied": [...],
            "final_avg_clv": 0.85,
            "final_avg_cart_value": 125.50
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request body is required'
            }), 400
        
        # Get the preview from the service
        preview = segment_service.preview_filter_impact(
            data.get('campaign_objective_object'),
            data.get('new_filters', {}),
            data.get('selected_trigger')  # Pass trigger to apply sensitivity filter
        )
        
        return jsonify(preview.model_dump()), 200
        
    except Exception as e:
        print(f"Error in preview_filter_impact: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@api.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404


@api.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

