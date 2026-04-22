"""
Post scheduling module for managing and automating social media posts
"""

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict
import schedule
from database import Database

class PostScheduler:
    def __init__(self, db: Database):
        """Initialize the scheduler with database connection"""
        self.db = db
        self.scheduler_thread = None
        self.is_running = False
        
    def start_scheduler(self):
        """Start the background scheduler thread"""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            print("Post scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        print("Post scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop running in background"""
        # Check for pending posts every minute
        schedule.every(1).minutes.do(self._check_and_post)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_and_post(self):
        """Check for posts that need to be published"""
        current_time = datetime.now()
        
        # Get all pending posts
        pending_posts = self.db.get_scheduled_posts(status='pending')
        
        for post in pending_posts:
            scheduled_time = datetime.strptime(post['scheduled_time'], '%Y-%m-%d %H:%M:%S')
            
            # If scheduled time has passed, publish the post
            if scheduled_time <= current_time:
                success = self._publish_post(post)
                
                if success:
                    # Update status to published
                    self.db.update_post_status(post['id'], 'published')
                    print(f"Published post {post['id']} to {post['platform']}")
                else:
                    # Mark as failed if publishing fails
                    self.db.update_post_status(post['id'], 'failed')
                    print(f"Failed to publish post {post['id']}")
    
    def _publish_post(self, post: Dict) -> bool:
        """
        Simulate publishing a post to social media platform
        In a real implementation, this would call actual platform APIs
        """
        try:
            # Simulate API call delay
            time.sleep(0.5)
            
            # Generate mock analytics data for the post
            import random
            analytics_data = {
                'platform': post['platform'],
                'post_content': post['content'],
                'likes': random.randint(10, 500),
                'shares': random.randint(0, 100),
                'comments': random.randint(0, 50),
                'impressions': random.randint(100, 5000)
            }
            
            # Save analytics data
            self.db.add_post_analytics(**analytics_data)
            
            return True
            
        except Exception as e:
            print(f"Error publishing post: {e}")
            return False
    
    def schedule_post(self, content: str, platform: str, 
                     schedule_time: str) -> Dict:
        """
        Schedule a post for future publishing
        
        Args:
            content: Post content
            platform: Target platform
            schedule_time: Time string in format 'YYYY-MM-DD HH:MM:SS'
        
        Returns:
            Dictionary with scheduling result
        """
        try:
            # Validate schedule time
            scheduled_datetime = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M:%S')
            
            if scheduled_datetime <= datetime.now():
                return {
                    'success': False,
                    'error': 'Schedule time must be in the future'
                }
            
            # Add to database
            post_id = self.db.add_scheduled_post(content, platform, schedule_time)
            
            return {
                'success': True,
                'post_id': post_id,
                'scheduled_time': schedule_time,
                'platform': platform
            }
            
        except ValueError:
            return {
                'success': False,
                'error': 'Invalid time format. Use YYYY-MM-DD HH:MM:SS'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upcoming_posts(self, limit: int = 10) -> List[Dict]:
        """Get upcoming scheduled posts"""
        all_posts = self.db.get_scheduled_posts(status='pending')
        current_time = datetime.now()
        
        # Filter for future posts and sort by time
        future_posts = [
            post for post in all_posts 
            if datetime.strptime(post['scheduled_time'], '%Y-%m-%d %H:%M:%S') > current_time
        ]
        
        # Sort by scheduled time
        future_posts.sort(key=lambda x: x['scheduled_time'])
        
        return future_posts[:limit]
    
    def get_post_history(self, limit: int = 20) -> List[Dict]:
        """Get history of published posts"""
        return self.db.get_scheduled_posts(status='published')[:limit]
    
    def cancel_scheduled_post(self, post_id: int) -> Dict:
        """Cancel a scheduled post"""
        try:
            # Get the post first to check if it's pending
            posts = self.db.get_scheduled_posts()
            post = next((p for p in posts if p['id'] == post_id), None)
            
            if not post:
                return {'success': False, 'error': 'Post not found'}
            
            if post['status'] != 'pending':
                return {'success': False, 'error': f"Cannot cancel post with status: {post['status']}"}
            
            # Delete the post
            self.db.delete_scheduled_post(post_id)
            
            return {'success': True, 'message': f'Post {post_id} cancelled successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}