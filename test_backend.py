"""
Quick test script to debug segment size issue
Run with: python test_backend.py
"""

import requests
import json

# Test the backend
API_URL = "http://localhost:5000/api/v1"

def test_campaign_analysis():
    """Test campaign analysis endpoint"""
    
    print("=" * 60)
    print("Testing Campaign Analysis Endpoint")
    print("=" * 60)
    
    # Test data
    objective = "Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers"
    
    print(f"\n📝 Campaign Objective:")
    print(f"   {objective}")
    
    # Make request
    print(f"\n🔄 Sending POST request to {API_URL}/campaigns/analyze...")
    
    try:
        response = requests.post(
            f"{API_URL}/campaigns/analyze",
            json={"objective": objective},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Response received successfully!")
            print(f"\n📋 Response Structure:")
            print(f"   Keys: {list(data.keys())}")
            
            # Check segment preview
            if 'segment_preview' in data:
                preview = data['segment_preview']
                print(f"\n📊 Segment Preview:")
                print(f"   Segment ID: {preview.get('segment_id', 'N/A')}")
                print(f"   Estimated Size: {preview.get('estimated_size', 'N/A')}")
                print(f"   Avg CLV Score: {preview.get('avg_clv_score', 'N/A')}")
                print(f"   Predicted Uplift: {preview.get('predicted_uplift', 'N/A')}")
                print(f"   Predicted ROI: {preview.get('predicted_roi', 'N/A')}")
                print(f"   Avg Cart Value: {preview.get('avg_cart_value', 'N/A')}")
                
                # Check AI filters
                if 'ai_filters' in preview:
                    filters = preview['ai_filters']
                    print(f"\n🤖 AI Filters ({len(filters)}):")
                    for i, f in enumerate(filters, 1):
                        print(f"   {i}. {f.get('filter_type', 'N/A')}: {f.get('description', 'N/A')}")
                else:
                    print(f"\n⚠️  No ai_filters field in segment_preview")
            else:
                print(f"\n❌ No segment_preview in response")
            
            # Check triggers
            if 'trigger_suggestions' in data:
                triggers = data['trigger_suggestions']
                print(f"\n🎯 Trigger Suggestions ({len(triggers)}):")
                for i, t in enumerate(triggers[:3], 1):
                    print(f"   {i}. {t.get('trigger_name', 'N/A')}: {t.get('predicted_uplift', 'N/A')} uplift")
            
            # Save full response for inspection
            with open('test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to test_response.json")
            
        else:
            print(f"\n❌ Error Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {API_URL}")
        print(f"   Make sure the backend server is running (python run.py)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_health():
    """Test health endpoint"""
    
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"\n📊 Health Check Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   Service: {data.get('service', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Backend server is not running")
        print(f"   Start it with: python run.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 AetherSegment AI Backend Test")
    print("=" * 60)
    
    # Test health first
    test_health()
    
    # Test campaign analysis
    test_campaign_analysis()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check the terminal where backend is running for detailed logs")
    print("2. Review test_response.json for the full API response")
    print("3. Look for any error messages or unexpected values")
    print()

