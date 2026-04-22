"""
Database module for handling all database operations
Uses SQLite for local storage of posts and analytics
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path="social_media.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Create and return a database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create all necessary tables for the application"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table for scheduled posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                platform TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for post analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_content TEXT,
                platform TEXT NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0
            )
        ''')
        
        # Table for content ideas history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                idea TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Post scheduling methods
    def add_scheduled_post(self, content: str, platform: str, scheduled_time: str) -> int:
        """Add a new scheduled post to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_posts (content, platform, scheduled_time)
            VALUES (?, ?, ?)
        ''', (content, platform, scheduled_time))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_id
    
    def get_scheduled_posts(self, status: str = None) -> List[Dict]:
        """Retrieve scheduled posts, optionally filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT id, content, platform, scheduled_time, status, created_at
                FROM scheduled_posts
                WHERE status = ?
                ORDER BY scheduled_time ASC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT id, content, platform, scheduled_time, status, created_at
                FROM scheduled_posts
                ORDER BY scheduled_time ASC
            ''')
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'content': row[1],
                'platform': row[2],
                'scheduled_time': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return posts
    
    def update_post_status(self, post_id: int, status: str):
        """Update the status of a scheduled post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_posts
            SET status = ?
            WHERE id = ?
        ''', (status, post_id))
        
        conn.commit()
        conn.close()
    
    def delete_scheduled_post(self, post_id: int):
        """Delete a scheduled post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scheduled_posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
    
    # Analytics methods
    def add_post_analytics(self, platform: str, post_content: str = "", 
                          likes: int = 0, shares: int = 0, 
                          comments: int = 0, impressions: int = 0) -> int:
        """Add analytics data for a posted content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO post_analytics (platform, post_content, likes, shares, comments, impressions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (platform, post_content, likes, shares, comments, impressions))
        
        analytics_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analytics_id
    
    def get_analytics_summary(self) -> Dict:
        """Get summary statistics from analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get total posts
        cursor.execute('SELECT COUNT(*) FROM post_analytics')
        total_posts = cursor.fetchone()[0]
        
        # Get total engagement
        cursor.execute('''
            SELECT SUM(likes), SUM(shares), SUM(comments), SUM(impressions)
            FROM post_analytics
        ''')
        result = cursor.fetchone()
        total_likes = result[0] or 0
        total_shares = result[1] or 0
        total_comments = result[2] or 0
        total_impressions = result[3] or 0
        
        # Get platform breakdown
        cursor.execute('''
            SELECT platform, COUNT(*) as count, AVG(likes) as avg_likes
            FROM post_analytics
            GROUP BY platform
        ''')
        platform_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_posts': total_posts,
            'total_likes': total_likes,
            'total_shares': total_shares,
            'total_comments': total_comments,
            'total_impressions': total_impressions,
            'total_engagement': total_likes + total_shares + total_comments,
            'platform_stats': platform_stats
        }
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts for analytics display"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, platform, post_content, posted_at, likes, shares, comments, impressions
            FROM post_analytics
            ORDER BY posted_at DESC
            LIMIT ?
        ''', (limit,))
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'platform': row[1],
                'content': row[2][:100] + '...' if len(row[2] or '') > 100 else row[2],
                'posted_at': row[3],
                'likes': row[4],
                'shares': row[5],
                'comments': row[6],
                'impressions': row[7]
            })
        
        conn.close()
        return posts
    
    # Content ideas methods
    def save_content_ideas(self, niche: str, ideas: List[str]):
        """Save generated content ideas to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for idea in ideas:
            cursor.execute('''
                INSERT INTO content_ideas (niche, idea)
                VALUES (?, ?)
            ''', (niche, idea))
        
        conn.commit()
        conn.close()
    
    def get_content_ideas_history(self, niche: str = None, limit: int = 20) -> List[Dict]:
        """Retrieve content ideas history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if niche:
            cursor.execute('''
                SELECT niche, idea, created_at
                FROM content_ideas
                WHERE niche = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (niche, limit))
        else:
            cursor.execute('''
                SELECT niche, idea, created_at
                FROM content_ideas
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        ideas = []
        for row in cursor.fetchall():
            ideas.append({
                'niche': row[0],
                'idea': row[1],
                'created_at': row[2]
            })
        
        conn.close()
        return ideas