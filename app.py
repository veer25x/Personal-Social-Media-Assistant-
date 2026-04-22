"""
Main Flask application for Personal Social Media Assistant
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
import secrets

from database import Database
from content_generator import ContentGenerator
from scheduler import PostScheduler
from analytics import Analytics
from reply_generator import ReplyGenerator

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize components
db = Database()
content_gen = ContentGenerator(api_key=os.getenv('OPENAI_API_KEY'))
scheduler = PostScheduler(db)
analytics = Analytics(db)
reply_gen = ReplyGenerator()

# Start the scheduler in background
scheduler.start_scheduler()

# Routes
@app.route('/')
def index():
    """Home page - Dashboard"""
    # Get upcoming posts for dashboard
    upcoming_posts = scheduler.get_upcoming_posts(limit=5)
    
    # Get recent analytics for quick stats
    analytics_data = analytics.get_dashboard_data()
    
    return render_template('index.html', 
                         upcoming_posts=upcoming_posts,
                         analytics=analytics_data['summary'])

@app.route('/generate', methods=['POST'])
def generate_content():
    """Generate social media content"""
    try:
        data = request.json
        topic = data.get('topic', '')
        platform = data.get('platform', 'twitter')
        tone = data.get('tone', 'casual')
        audience = data.get('audience', 'general')
        goal = data.get('goal', 'awareness')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Generate post
        post = content_gen.generate_post(topic, platform, tone, audience, goal)
        
        # Generate caption
        caption = content_gen.generate_caption(post['content'], platform, tone)
        
        return jsonify({
            'success': True,
            'post': post,
            'caption': caption
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hashtags', methods=['POST'])
def generate_hashtags():
    """Generate hashtags for a topic"""
    try:
        data = request.json
        topic = data.get('topic', '')
        platform = data.get('platform', 'instagram')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        hashtags = content_gen.generate_hashtags(topic, platform)
        
        return jsonify({
            'success': True,
            'hashtags': hashtags
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/schedule', methods=['GET', 'POST'])
def schedule_post():
    """Schedule a post page and API endpoint"""
    if request.method == 'GET':
        # Get all scheduled posts
        pending_posts = scheduler.get_upcoming_posts(limit=20)
        published_posts = scheduler.get_post_history(limit=10)
        
        return render_template('schedule.html',
                             pending_posts=pending_posts,
                             published_posts=published_posts)
    
    elif request.method == 'POST':
        data = request.json
        content = data.get('content', '')
        platform = data.get('platform', 'twitter')
        schedule_time = data.get('schedule_time', '')
        
        if not content or not schedule_time:
            return jsonify({'error': 'Content and schedule time are required'}), 400
        
        result = scheduler.schedule_post(content, platform, schedule_time)
        
        return jsonify(result)

@app.route('/schedule/cancel/<int:post_id>', methods=['DELETE'])
def cancel_scheduled_post(post_id):
    """Cancel a scheduled post"""
    result = scheduler.cancel_scheduled_post(post_id)
    return jsonify(result)

@app.route('/analytics')
def analytics_dashboard():
    """Analytics dashboard page"""
    data = analytics.get_dashboard_data()
    insights = analytics.get_insights()
    
    return render_template('analytics.html',
                         data=data,
                         insights=insights)

@app.route('/analytics/add', methods=['POST'])
def add_analytics():
    """Add manual analytics data"""
    try:
        data = request.json
        result = analytics.add_engagement_data(
            post_id=data.get('post_id'),
            likes=data.get('likes', 0),
            shares=data.get('shares', 0),
            comments=data.get('comments', 0),
            impressions=data.get('impressions', 0)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/replies', methods=['GET', 'POST'])
def generate_replies():
    """Reply generator page and API"""
    if request.method == 'GET':
        return render_template('replies.html')
    
    elif request.method == 'POST':
        data = request.json
        comments = data.get('comments', [])
        tone = data.get('tone', 'friendly')
        
        if not comments:
            return jsonify({'error': 'Comments are required'}), 400
        
        if isinstance(comments, str):
            # Single comment
            reply = reply_gen.generate_reply(comments, tone)
            return jsonify({
                'success': True,
                'reply': reply
            })
        else:
            # Multiple comments
            replies = reply_gen.generate_bulk_replies(comments, tone)
            return jsonify({
                'success': True,
                'replies': replies
            })

@app.route('/ideas', methods=['POST'])
def generate_ideas():
    """Generate content ideas"""
    try:
        data = request.json
        niche = data.get('niche', '')
        count = data.get('count', 10)
        
        if not niche:
            return jsonify({'error': 'Niche is required'}), 400
        
        ideas = content_gen.generate_content_ideas(niche, count)
        
        # Save ideas to database
        db.save_content_ideas(niche, ideas)
        
        return jsonify({
            'success': True,
            'ideas': ideas,
            'niche': niche
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/ideas')
def ideas_history():
    """Get content ideas history"""
    niche = request.args.get('niche')
    ideas = db.get_content_ideas_history(niche)
    return jsonify({'success': True, 'ideas': ideas})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error="Internal server error"), 500

# Cleanup on shutdown
import atexit
@atexit.register
def cleanup():
    scheduler.stop_scheduler()

if __name__ == '__main__':
    app.run(debug=True, port=5000)