"""
Analytics module for tracking and visualizing social media performance
"""

from datetime import datetime, timedelta
from typing import Dict, List
from database import Database

class Analytics:
    def __init__(self, db: Database):
        """Initialize analytics with database connection"""
        self.db = db
    
    def get_dashboard_data(self) -> Dict:
        """Get all data needed for the analytics dashboard"""
        
        # Get summary statistics
        summary = self.db.get_analytics_summary()
        
        # Get recent posts
        recent_posts = self.db.get_recent_posts(limit=10)
        
        # Calculate engagement rate
        engagement_rate = 0
        if summary['total_impressions'] > 0:
            engagement_rate = (summary['total_engagement'] / summary['total_impressions']) * 100
        
        # Calculate average engagement per post
        avg_engagement = 0
        if summary['total_posts'] > 0:
            avg_engagement = summary['total_engagement'] / summary['total_posts']
        
        # Get platform-specific metrics
        platform_metrics = []
        for platform, count, avg_likes in summary['platform_stats']:
            platform_metrics.append({
                'platform': platform,
                'post_count': count,
                'avg_likes': round(avg_likes or 0, 1),
                'engagement_score': round((avg_likes or 0) * 0.5, 1)  # Simplified scoring
            })
        
        # Get weekly trend (last 7 days)
        weekly_trend = self._get_weekly_trend()
        
        # Get best performing posts
        best_posts = self._get_best_performing_posts(limit=5)
        
        return {
            'summary': {
                'total_posts': summary['total_posts'],
                'total_engagement': summary['total_engagement'],
                'total_impressions': summary['total_impressions'],
                'avg_engagement_per_post': round(avg_engagement, 1),
                'engagement_rate': round(engagement_rate, 1),
                'total_likes': summary['total_likes'],
                'total_shares': summary['total_shares'],
                'total_comments': summary['total_comments']
            },
            'platform_metrics': platform_metrics,
            'weekly_trend': weekly_trend,
            'best_posts': best_posts,
            'recent_posts': recent_posts
        }
    
    def _get_weekly_trend(self) -> Dict:
        """Calculate engagement trend for the last 7 days"""
        trend = {
            'dates': [],
            'engagement': [],
            'posts_count': []
        }
        
        # Get data for last 7 days
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Get posts from this date
            cursor.execute('''
                SELECT COUNT(*), SUM(likes + shares + comments)
                FROM post_analytics
                WHERE DATE(posted_at) = ?
            ''', (date_str,))
            
            result = cursor.fetchone()
            post_count = result[0] or 0
            engagement = result[1] or 0
            
            trend['dates'].append(date.strftime('%b %d'))
            trend['engagement'].append(engagement)
            trend['posts_count'].append(post_count)
        
        conn.close()
        
        return trend
    
    def _get_best_performing_posts(self, limit: int = 5) -> List[Dict]:
        """Get the best performing posts based on engagement"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, platform, post_content, likes, shares, comments, impressions, posted_at,
                   (likes + shares + comments) as total_engagement
            FROM post_analytics
            ORDER BY total_engagement DESC
            LIMIT ?
        ''', (limit,))
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row[0],
                'platform': row[1],
                'content': row[2][:100] + '...' if row[2] and len(row[2]) > 100 else row[2],
                'likes': row[3],
                'shares': row[4],
                'comments': row[5],
                'impressions': row[6],
                'posted_at': row[7],
                'total_engagement': row[8]
            })
        
        conn.close()
        return posts
    
    def add_engagement_data(self, post_id: int, likes: int = 0, 
                           shares: int = 0, comments: int = 0,
                           impressions: int = 0) -> Dict:
        """Manually add or update engagement data for a post"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if post exists
            cursor.execute('SELECT id FROM post_analytics WHERE id = ?', (post_id,))
            if not cursor.fetchone():
                return {'success': False, 'error': 'Post not found'}
            
            # Update engagement data
            cursor.execute('''
                UPDATE post_analytics
                SET likes = ?, shares = ?, comments = ?, impressions = ?
                WHERE id = ?
            ''', (likes, shares, comments, impressions, post_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Engagement data updated'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_insights(self) -> List[str]:
        """Generate actionable insights from analytics data"""
        insights = []
        data = self.get_dashboard_data()
        
        # Insight 1: Best performing platform
        if data['platform_metrics']:
            best_platform = max(data['platform_metrics'], 
                              key=lambda x: x['engagement_score'])
            insights.append(f"📈 Your best performing platform is {best_platform['platform'].upper()} "
                          f"with an engagement score of {best_platform['engagement_score']}")
        
        # Insight 2: Engagement rate
        if data['summary']['engagement_rate'] > 5:
            insights.append(f"🎯 Great engagement rate of {data['summary']['engagement_rate']}%! "
                          "Your content is resonating well with your audience.")
        elif data['summary']['engagement_rate'] > 2:
            insights.append(f"📊 Your engagement rate is {data['summary']['engagement_rate']}%. "
                          "Try posting more interactive content to boost engagement.")
        else:
            insights.append(f"⚠️ Your engagement rate is {data['summary']['engagement_rate']}%. "
                          "Consider optimizing your content strategy.")
        
        # Insight 3: Posting consistency
        if data['summary']['total_posts'] > 20:
            insights.append("💪 Great consistency! You're posting regularly which helps with algorithm favorability.")
        elif data['summary']['total_posts'] > 10:
            insights.append("📅 You're on the right track with posting frequency. "
                          "Try to maintain a consistent schedule.")
        else:
            insights.append("🚀 Increase your posting frequency to see better growth and engagement.")
        
        # Insight 4: Best performing content type
        if data['best_posts']:
            best_post_platform = data['best_posts'][0]['platform']
            insights.append(f"⭐ Your top-performing content comes from {best_post_platform.upper()}. "
                          "Analyze what made it successful and replicate that formula.")
        
        # Insight 5: Weekly trend
        if data['weekly_trend']['engagement']:
            recent_engagement = data['weekly_trend']['engagement'][-3:]
            if len(recent_engagement) >= 2 and recent_engagement[-1] > recent_engagement[-2]:
                insights.append("📈 Your engagement is trending upward! Keep up the great work!")
            elif len(recent_engagement) >= 2 and recent_engagement[-1] < recent_engagement[-2]:
                insights.append("📉 Engagement has decreased recently. Try experimenting with different content formats.")
        
        return insights