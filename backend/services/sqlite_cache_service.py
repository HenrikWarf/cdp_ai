"""
SQLite Cache Service for Overview Dashboard
Provides persistent caching to improve performance and reduce BigQuery costs
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class SQLiteCacheService:
    """
    Service for managing SQLite-based caching of overview dashboard data
    """
    
    def __init__(self, db_path: str = 'backend/data/cache.db'):
        """
        Initialize SQLite cache service
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self.initialize_database()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS overview_cache (
                id INTEGER PRIMARY KEY,
                metrics TEXT NOT NULL,
                geographic_distribution TEXT,
                value_segments TEXT,
                opportunities TEXT,
                behavioral_insights TEXT,
                data_health TEXT,
                last_updated TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ SQLite cache database initialized at: {self.db_path}")
    
    def is_cache_populated(self) -> bool:
        """
        Check if cache has any data
        
        Returns:
            True if cache has data, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM overview_cache')
        result = cursor.fetchone()
        count = result['count']
        
        conn.close()
        return count > 0
    
    def get_overview_data(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached overview data
        
        Returns:
            Dictionary with overview data or None if cache is empty
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                metrics,
                geographic_distribution,
                value_segments,
                opportunities,
                behavioral_insights,
                data_health,
                last_updated
            FROM overview_cache
            ORDER BY id DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Parse JSON strings back to dictionaries/lists
        data = {
            'metrics': json.loads(row['metrics']),
            'geographic_distribution': json.loads(row['geographic_distribution']) if row['geographic_distribution'] else {},
            'value_segments': json.loads(row['value_segments']) if row['value_segments'] else {},
            'opportunities': json.loads(row['opportunities']) if row['opportunities'] else [],
            'behavioral_insights': json.loads(row['behavioral_insights']) if row['behavioral_insights'] else [],
            'data_health': json.loads(row['data_health']) if row['data_health'] else {},
            'last_updated': row['last_updated']
        }
        
        return data
    
    def save_overview_data(self, data: Dict[str, Any]) -> None:
        """
        Save/update overview data (keeps only the latest entry)
        
        Args:
            data: Dictionary containing overview statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Delete old data (keep only 1 row)
        cursor.execute('DELETE FROM overview_cache')
        
        # Insert new data
        cursor.execute('''
            INSERT INTO overview_cache (
                metrics,
                geographic_distribution,
                value_segments,
                opportunities,
                behavioral_insights,
                data_health,
                last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            json.dumps(data.get('metrics', {})),
            json.dumps(data.get('geographic_distribution', {})),
            json.dumps(data.get('value_segments', {})),
            json.dumps(data.get('opportunities', [])),
            json.dumps(data.get('behavioral_insights', [])),
            json.dumps(data.get('data_health', {})),
            data.get('last_updated', datetime.utcnow().isoformat())
        ))
        
        conn.commit()
        conn.close()
        print(f"💾 Overview data saved to SQLite cache")
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM overview_cache')
        
        conn.commit()
        conn.close()
        print("🗑️ SQLite cache cleared")

