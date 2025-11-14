"""
Startup script for Conversational Segmentation Agent
Run this from the project root: python run_segmentation.py
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add conversational_segmentation to Python path
segmentation_path = project_root / "conversational_segmentation"
sys.path.insert(0, str(segmentation_path))


def check_environment():
    """Check if required environment variables exist"""
    from dotenv import load_dotenv
    
    # Load environment variables from conversational_segmentation/.env
    env_path = segmentation_path / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Check for GOOGLE_CLOUD_PROJECT or BIGQUERY_PROJECT (use either)
    bigquery_project = os.getenv('BIGQUERY_PROJECT') or os.getenv('GOOGLE_CLOUD_PROJECT')
    bigquery_dataset = os.getenv('BIGQUERY_DATASET')
    bigquery_table = os.getenv('BIGQUERY_TABLE')
    
    # Set BIGQUERY_PROJECT from GOOGLE_CLOUD_PROJECT if needed
    if bigquery_project and not os.getenv('BIGQUERY_PROJECT'):
        os.environ['BIGQUERY_PROJECT'] = bigquery_project
    
    missing_vars = []
    if not bigquery_project:
        missing_vars.append('GOOGLE_CLOUD_PROJECT or BIGQUERY_PROJECT')
    if not bigquery_dataset:
        missing_vars.append('BIGQUERY_DATASET')
    if not bigquery_table:
        missing_vars.append('BIGQUERY_TABLE')
    
    if missing_vars:
        print("\n❌ Configuration Error:")
        print(f"   Missing required environment variables: {', '.join(missing_vars)}\n")
        print("Please add to your .env file:")
        if not bigquery_project:
            print(f"  GOOGLE_CLOUD_PROJECT=your-gcp-project-id")
        if not bigquery_dataset:
            print(f"  BIGQUERY_DATASET=customer_data_retail  # your dataset name")
        if not bigquery_table:
            print(f"  BIGQUERY_TABLE=customer  # your table name")
        print("\n")
        return False
    
    # Check if service account file exists (if specified)
    sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if sa_path:
        # Resolve path relative to conversational_segmentation folder
        if not os.path.isabs(sa_path):
            resolved_path = (segmentation_path / sa_path).resolve()
        else:
            resolved_path = Path(sa_path)
        
        if not resolved_path.is_file():
            print(f"\n⚠️  Warning: Service account file not found: {sa_path}")
            print(f"    Resolved to: {resolved_path}")
            print("    Attempting to use Application Default Credentials...\n")
        else:
            # Update the environment variable with the resolved absolute path
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(resolved_path)
    
    return True


if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("  💬 Conversational Segmentation Agent Starting...")
        print("="*60)
        
        # Validate environment
        if not check_environment():
            sys.exit(1)
        
        print("  ✓ Configuration validated")
        print(f"  GCP Project: {os.getenv('BIGQUERY_PROJECT') or os.getenv('GOOGLE_CLOUD_PROJECT')}")
        print(f"  Dataset: {os.getenv('BIGQUERY_DATASET')}")
        print(f"  Table: {os.getenv('BIGQUERY_TABLE')}")
        print("="*60 + "\n")
        
        # Import and run uvicorn
        import uvicorn
        
        print("Starting FastAPI server on port 8001...")
        print("Access the segmentation UI at: http://localhost:8001")
        print("Frontend will connect from: http://localhost:5500")
        print("\nPress Ctrl+C to stop the server.\n")
        
        # Import the app from the conversational_segmentation module
        # We need to run it from the conversational_segmentation directory
        # so the static files are found correctly
        original_dir = os.getcwd()
        os.chdir(segmentation_path)
        
        try:
            from api import app
            
            # Run the FastAPI application
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8001,
                log_level="info"
            )
        finally:
            # Restore original directory
            os.chdir(original_dir)
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n✓ Conversational segmentation agent stopped by user.\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error starting conversational segmentation agent: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

