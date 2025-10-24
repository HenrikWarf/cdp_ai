"""
Simple startup script for AetherSegment AI
Run this from the project root: python run.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app import create_app
from backend.config import Config

if __name__ == '__main__':
    try:
        # Validate configuration
        Config.validate()
        
        # Create and run the app
        app = create_app()
        
        print("\n" + "="*60)
        print("  🚀 AetherSegment AI Starting...")
        print("="*60)
        print(f"  Environment: {Config.FLASK_ENV}")
        print(f"  Port: {Config.FLASK_PORT}")
        print(f"  Debug: {Config.FLASK_DEBUG}")
        print(f"  GCP Project: {Config.GOOGLE_CLOUD_PROJECT}")
        print(f"  BigQuery Dataset: {Config.BIGQUERY_DATASET}")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
        
    except ValueError as e:
        print("\n❌ Configuration Error:")
        print(f"   {str(e)}\n")
        print("Please create a .env file with the following variables:")
        print("  GOOGLE_CLOUD_PROJECT=your-project-id")
        print("  GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json")
        print("  (See .env.example or README.md for full configuration)\n")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

