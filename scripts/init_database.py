#!/usr/bin/env python3
"""
Database initialization script for Social Media Agent.

This script creates the necessary database tables and initial data
for the Social Media Agent system.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_sqlite_database(db_path: str):
    """Create SQLite database with necessary tables."""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'stopped',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                post_id TEXT,
                content TEXT,
                content_type TEXT DEFAULT 'text',
                status TEXT DEFAULT 'pending',
                scheduled_for TIMESTAMP,
                posted_at TIMESTAMP,
                engagement_count INTEGER DEFAULT 0,
                likes_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_name) REFERENCES agents (name)
            )
        """)
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT DEFAULT 'counter',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_name) REFERENCES agents (name)
            )
        """)
        
        # Create reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                report_period_start TIMESTAMP,
                report_period_end TIMESTAMP,
                report_data TEXT,
                file_path TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_agent_platform ON metrics(agent_name, platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON metrics(recorded_at)")
        
        # Insert initial configuration
        initial_config = [
            ("system_initialized", "true", "System initialization flag"),
            ("database_version", "1.0", "Database schema version"),
            ("last_report_generated", "", "Timestamp of last generated report")
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO configuration (key, value, description) VALUES (?, ?, ?)",
            initial_config
        )
        
        # Commit changes
        conn.commit()
        print("✅ SQLite database initialized successfully")
        print(f"📁 Database location: {db_path}")
        
        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Created tables: {', '.join([table[0] for table in tables])}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


def main():
    """Main function."""
    # Default database path
    default_db_path = "data/social_media_agent.db"
    
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")
    
    if database_url.startswith("sqlite:///"):
        # Extract path from SQLite URL
        db_path = database_url.replace("sqlite:///", "")
        if not db_path.startswith("/"):
            # Relative path
            db_path = os.path.join(os.getcwd(), db_path)
        
        print(f"🗄️  Initializing SQLite database: {db_path}")
        create_sqlite_database(db_path)
        
    elif database_url.startswith("postgresql://"):
        print("🐘 PostgreSQL database detected")
        print("Please run the PostgreSQL initialization script separately")
        print("Or use the provided SQL files in the database/ directory")
        
    else:
        print(f"❌ Unsupported database URL: {database_url}")
        sys.exit(1)
    
    print("\n🎉 Database initialization completed!")
    print("You can now start the Social Media Agent system.")


if __name__ == "__main__":
    main()

