"""
Database layer for Screen Time Tracker
Handles SQLite database operations for storing usage data
"""
import sqlite3
import os
from datetime import datetime, date
from pathlib import Path


class Database:
    """Database manager for screen time tracking"""
    
    def __init__(self, db_path=None):
        """Initialize database connection"""
        if db_path is None:
            # Store in user's AppData folder
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            db_dir = Path(appdata) / 'ScreenTimeTracker'
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / 'screentime.db'
        
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def init_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Create app_usage table for tracking per-application time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                app_name TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, app_name)
            )
        ''')
        
        # Create sessions table for daily summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_seconds INTEGER NOT NULL DEFAULT 0,
                app_count INTEGER NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_app_usage_date 
            ON app_usage(date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_app_usage_app 
            ON app_usage(app_name)
        ''')
        
        self.conn.commit()
    
    def record_app_usage(self, app_name, duration_seconds):
        """Record or update app usage for today"""
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        
        # Insert or update app usage
        cursor.execute('''
            INSERT INTO app_usage (date, app_name, duration_seconds, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(date, app_name) 
            DO UPDATE SET 
                duration_seconds = duration_seconds + ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (today, app_name, duration_seconds, duration_seconds))
        
        # Update daily session summary
        cursor.execute('''
            INSERT INTO sessions (date, total_seconds, app_count, last_updated)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(date) 
            DO UPDATE SET 
                total_seconds = total_seconds + ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (today, duration_seconds, duration_seconds))
        
        self.conn.commit()
    
    def get_today_stats(self):
        """Get today's statistics"""
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        
        # Get total time today
        cursor.execute('''
            SELECT total_seconds FROM sessions WHERE date = ?
        ''', (today,))
        row = cursor.fetchone()
        total_seconds = row[0] if row else 0
        
        # Get top apps today
        cursor.execute('''
            SELECT app_name, duration_seconds
            FROM app_usage
            WHERE date = ?
            ORDER BY duration_seconds DESC
            LIMIT 10
        ''', (today,))
        
        top_apps = [{'app_name': row[0], 'duration': row[1]} 
                    for row in cursor.fetchall()]
        
        return {
            'total_seconds': total_seconds,
            'top_apps': top_apps
        }
    
    def get_weekly_stats(self):
        """Get weekly statistics"""
        cursor = self.conn.cursor()
        
        # Get last 7 days
        cursor.execute('''
            SELECT date, total_seconds
            FROM sessions
            WHERE date >= date('now', '-7 days')
            ORDER BY date ASC
        ''')
        
        daily_stats = [{'date': row[0], 'total_seconds': row[1]} 
                      for row in cursor.fetchall()]
        
        # Get top apps for the week
        cursor.execute('''
            SELECT app_name, SUM(duration_seconds) as total_duration
            FROM app_usage
            WHERE date >= date('now', '-7 days')
            GROUP BY app_name
            ORDER BY total_duration DESC
            LIMIT 10
        ''')
        
        top_apps = [{'app_name': row[0], 'duration': row[1]} 
                   for row in cursor.fetchall()]
        
        return {
            'daily_stats': daily_stats,
            'top_apps': top_apps
        }
    
    def get_app_history(self, app_name, days=30):
        """Get usage history for a specific app"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT date, duration_seconds
            FROM app_usage
            WHERE app_name = ? AND date >= date('now', '-' || ? || ' days')
            ORDER BY date ASC
        ''', (app_name, days))
        
        return [{'date': row[0], 'duration': row[1]} 
               for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

