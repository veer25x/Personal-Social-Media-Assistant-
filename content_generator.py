"""
Content generation module using OpenAI API
Includes fallback mock responses for testing without API key
"""

import random
from typing import Dict, List
import openai

class ContentGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the content generator with OpenAI API key"""
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
        self.use_mock = not api_key
        
        # Platform-specific character limits
        self.platform_limits = {
            'twitter': 280,
            'linkedin': 3000,
            'instagram': 2200
        }
        
        # Tone-specific templates
        self.tone_templates = {
            'professional': {
                'twitter': "Here's a professional insight: {topic}",
                'linkedin': "I'd like to share a professional perspective on {topic}",
                'instagram': "Professional tip: {topic}"
            },
            'casual': {
                'twitter': "Hey! Just thinking about {topic}...",
                'linkedin': "Let's talk casually about {topic}",
                'instagram': "Just sharing some thoughts on {topic} 💭"
            },
            'viral': {
                'twitter': "🔥 HOT TAKE: {topic}",
                'linkedin': "The truth about {topic} that nobody talks about!",
                'instagram': "THIS CHANGES EVERYTHING about {topic} 😱"
            },
            'motivational': {
                'twitter': "Believe in yourself! {topic} is possible! 💪",
                'linkedin': "Your journey with {topic} starts with one step",
                'instagram': "You've got this! Keep pushing forward with {topic} ✨"
            }
        }
        
        # Hashtag templates by niche
        self.hashtag_templates = {
            'technology': ['#Tech', '#Innovation', '#AI', '#Future', '#DigitalTransformation'],
            'marketing': ['#MarketingStrategy', '#DigitalMarketing', '#Growth', '#SocialMedia', '#Branding'],
            'fitness': ['#FitnessMotivation', '#Workout', '#HealthyLifestyle', '#GymLife', '#Wellness'],
            'business': ['#Entrepreneurship', '#BusinessGrowth', '#Success', '#Leadership', '#Startup'],
            'education': ['#Learning', '#Education', '#Knowledge', '#Skills', '#GrowthMindset'],
            'default': ['#SocialMedia', '#ContentCreation', '#DigitalPresence', '#Engagement', '#Growth']
        }
    
    def generate_post(self, topic: str, platform: str, tone: str, 
                     audience: str = "general", goal: str = "awareness") -> Dict:
        """
        Generate a social media post based on parameters
        
        Args:
            topic: The main subject of the post
            platform: twitter, linkedin, or instagram
            tone: professional, casual, viral, or motivational
            audience: Target audience description
            goal: Content goal (awareness, engagement, conversion)
        
        Returns:
            Dictionary containing generated post and metadata
        """
        
        if self.use_mock:
            return self._generate_mock_post(topic, platform, tone, audience, goal)
        else:
            return self._generate_ai_post(topic, platform, tone, audience, goal)
    
    def _generate_mock_post(self, topic: str, platform: str, tone: str,
                           audience: str, goal: str) -> Dict:
        """Generate mock posts when no API key is available"""
        
        # Get template for the tone and platform
        template = self.tone_templates.get(tone, self.tone_templates['casual'])
        platform_template = template.get(platform, template['twitter'])
        
        # Basic post structure
        base_post = platform_template.format(topic=topic)
        
        # Add audience and goal context
        if audience != "general":
            base_post += f" For {audience}..."
        
        if goal == "engagement":
            base_post += " What are your thoughts? 👇"
        elif goal == "conversion":
            base_post += " Click the link to learn more! 🔗"
        
        # Ensure character limit
        char_limit = self.platform_limits.get(platform, 280)
        if len(base_post) > char_limit:
            base_post = base_post[:char_limit-3] + "..."
        
        # Generate hashtags
        hashtags = self.generate_hashtags(topic, platform)
        
        # Add hashtags to post for Instagram and Twitter
        if platform in ['instagram', 'twitter']:
            full_post = f"{base_post}\n\n{hashtags}"
        else:
            full_post = base_post
        
        return {
            'content': full_post,
            'hashtags': hashtags,
            'platform': platform,
            'tone': tone,
            'character_count': len(full_post),
            'is_mock': True
        }
    
    def _generate_ai_post(self, topic: str, platform: str, tone: str,
                         audience: str, goal: str) -> Dict:
        """Generate post using OpenAI API"""
        
        prompt = f"""
        Create a {tone} social media post for {platform} about {topic}.
        Target audience: {audience}
        Goal: {goal}
        
        Requirements:
        - Keep within {self.platform_limits.get(platform, 280)} characters
        - Make it engaging and shareable
        - Include a call-to-action if appropriate
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            hashtags = self.generate_hashtags(topic, platform)
            
            if platform in ['instagram', 'twitter']:
                full_content = f"{content}\n\n{hashtags}"
            else:
                full_content = content
            
            return {
                'content': full_content,
                'hashtags': hashtags,
                'platform': platform,
                'tone': tone,
                'character_count': len(full_content),
                'is_mock': False
            }
            
        except Exception as e:
            # Fallback to mock generation if API fails
            return self._generate_mock_post(topic, platform, tone, audience, goal)
    
    def generate_hashtags(self, topic: str, platform: str, count: int = 5) -> str:
        """Generate relevant hashtags for the post"""
        
        # Determine niche from topic
        niche = 'default'
        topic_lower = topic.lower()
        
        niche_keywords = {
            'technology': ['tech', 'ai', 'software', 'coding', 'programming', 'digital'],
            'marketing': ['market', 'social media', 'brand', 'advertising', 'seo'],
            'fitness': ['fitness', 'workout', 'gym', 'exercise', 'health', 'wellness'],
            'business': ['business', 'startup', 'entrepreneur', 'company', 'corporate'],
            'education': ['learn', 'education', 'course', 'training', 'skill']
        }
        
        for niche_name, keywords in niche_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                niche = niche_name
                break
        
        # Get base hashtags for the niche
        base_hashtags = self.hashtag_templates.get(niche, self.hashtag_templates['default'])
        
        # Add topic-specific hashtag
        topic_hashtag = '#' + ''.join(word.capitalize() for word in topic.split()[:2])
        
        # Select random hashtags
        selected_hashtags = random.sample(base_hashtags, min(count-1, len(base_hashtags)))
        selected_hashtags.append(topic_hashtag)
        
        # Format hashtags
        if platform == 'instagram':
            return ' '.join(selected_hashtags)
        else:
            return ' '.join(selected_hashtags[:3])  # Fewer hashtags for other platforms
    
    def generate_caption(self, post_content: str, platform: str, tone: str) -> str:
        """Generate an optimized caption for the post"""
        
        captions = {
            'professional': {
                'twitter': "Professional insight: ",
                'linkedin': "📊 Professional perspective:\n\n",
                'instagram': "💼 Professional tip: "
            },
            'casual': {
                'twitter': "Just saying... ",
                'linkedin': "Hey everyone! 👋\n\n",
                'instagram': "Hey fam! 💫 "
            },
            'viral': {
                'twitter': "🚨 MUST READ: ",
                'linkedin': "🎯 The game-changer you need to see:\n\n",
                'instagram': "⚠️ THIS IS IMPORTANT ⚠️\n\n"
            },
            'motivational': {
                'twitter': "✨ Motivation: ",
                'linkedin': "💪 Your daily dose of motivation:\n\n",
                'instagram': "🌟 Keep pushing! 🌟\n\n"
            }
        }
        
        caption = captions.get(tone, captions['casual']).get(platform, "")
        
        # Add emojis based on tone
        emojis = {
            'professional': '📈',
            'casual': '😊',
            'viral': '🔥',
            'motivational': '💪'
        }
        
        caption += post_content[:200]  # First 200 characters as preview
        
        if len(post_content) > 200:
            caption += "..."
        
        caption += f"\n\n{emojis.get(tone, '✨')}"
        
        return caption

    def generate_content_ideas(self, niche: str, count: int = 10) -> List[str]:
        """Generate viral content ideas based on niche"""
        
        idea_templates = {
            'technology': [
                f"5 AI tools that will revolutionize {niche} in 2024",
                f"The future of {niche}: What experts are predicting",
                f"How to leverage blockchain in {niche}",
                f"Top 10 {niche} trends to watch this year",
                f"Why {niche} is the next big thing in tech",
                f"Beginners guide to mastering {niche}",
                f"The ethical implications of {niche}",
                f"How {niche} is changing the way we work",
                f"Case study: Successful {niche} implementation",
                f"Myths about {niche} debunked"
            ],
            'marketing': [
                f"7 days to master {niche} marketing",
                f"The psychology behind successful {niche} campaigns",
                f"How to create viral {niche} content",
                f"ROI of {niche}: Real numbers and case studies",
                f"Email marketing secrets for {niche}",
                f"Building a brand with {niche} strategies",
                f"The future of {niche} in a cookieless world",
                f"Influencer marketing for {niche} brands",
                f"SEO hacks for {niche} websites",
                f"Storytelling techniques for {niche}"
            ],
            'fitness': [
                f"30-day {niche} challenge for beginners",
                f"The science behind effective {niche} workouts",
                f"Nutrition tips to complement your {niche} routine",
                f"How to stay motivated with {niche}",
                f"Common {niche} mistakes and how to avoid them",
                f"At-home {niche} workouts for busy people",
                f"The mental health benefits of {niche}",
                f"Tracking progress in {niche}: What matters most",
                f"Recovery strategies for {niche} enthusiasts",
                f"Building a sustainable {niche} habit"
            ]
        }
        
        # Get templates for the niche or use generic ones
        templates = idea_templates.get(niche.lower(), 
            [f"10 ways to excel in {niche}",
             f"Why {niche} matters more than ever",
             f"Expert tips for mastering {niche}",
             f"The ultimate guide to {niche}",
             f"How {niche} is transforming our world",
             f"Success stories in {niche}",
             f"Common misconceptions about {niche}",
             f"The future trends in {niche}",
             f"Building a career in {niche}",
             f"Innovative approaches to {niche}"])
        
        # Return specified number of ideas
        if count <= len(templates):
            return templates[:count]
        else:
            # Duplicate templates if more ideas needed
            extended_ideas = templates.copy()
            while len(extended_ideas) < count:
                extended_ideas.extend([f"Advanced {niche} strategy #{i+1}" 
                                      for i in range(count - len(extended_ideas))])
            return extended_ideas[:count]