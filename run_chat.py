"""
Startup script for Conversational Analytics Agent
Run this from the project root: python run_chat.py
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add talk_to_data_advanced to Python path so agent imports work
talk_to_data_path = project_root / "talk_to_data_advanced"
sys.path.insert(0, str(talk_to_data_path))


def check_environment():
    """Check if required environment variables and files exist"""
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_APPLICATION_CREDENTIALS']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n❌ Configuration Error:")
        print(f"   Missing required environment variables: {', '.join(missing_vars)}\n")
        print("Please ensure your .env file contains:")
        for var in missing_vars:
            print(f"  {var}=your-value-here")
        print("\n")
        return False
    
    # Check if service account file exists
    sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not os.path.isfile(sa_path):
        print(f"\n❌ Service account file not found: {sa_path}")
        print("Please ensure the service account JSON file exists.\n")
        return False
    
    return True


if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("  🤖 Conversational Segmentation Agent Starting...")
        print("="*60)
        
        # Validate environment
        if not check_environment():
            sys.exit(1)
        
        print("  ✓ Configuration validated")
        print("  ✓ Service account credentials found")
        print(f"  GCP Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
        print("="*60 + "\n")
        
        # Import and run uvicorn
        import uvicorn
        
        print("Starting FastAPI server on port 8000...")
        print("Access the segmentation UI at: http://localhost:8000")
        print("Frontend will connect from: http://localhost:5500")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Import the app from the agent module
        from talk_to_data_advanced.agent.agent import app
        
        # Run the FastAPI application
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r talk_to_data_advanced/requirements.txt\n")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n✓ Conversational segmentation agent stopped by user.\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error starting conversational segmentation agent: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

