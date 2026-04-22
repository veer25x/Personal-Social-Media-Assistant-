"""
Reply generation module for comments and messages
"""

import random
from typing import Dict, List

class ReplyGenerator:
    def __init__(self):
        """Initialize reply generator with templates"""
        
        # Reply templates for different tones
        self.reply_templates = {
            'friendly': {
                'positive': [
                    "Thank you so much! 😊 Really appreciate your support!",
                    "Thanks for the kind words! 🙌",
                    "So glad you liked it! 💫",
                    "Thanks for engaging! Hope you found it valuable! ✨"
                ],
                'neutral': [
                    "Thanks for sharing your perspective! 😊",
                    "Interesting point! Thanks for the input! 💭",
                    "Appreciate you taking the time to comment! 🙏",
                    "Thanks for being part of the conversation! 🗣️"
                ],
                'question': [
                    "Great question! Here's what I think... 💭",
                    "Thanks for asking! Let me explain... 📝",
                    "That's an excellent question! In my experience... 🎯",
                    "I appreciate your curiosity! Here's my take... 💡"
                ]
            },
            'witty': {
                'positive': [
                    "Haha thanks! You're too kind 😎",
                    "Right?! That's what I've been saying! 🔥",
                    "Finally someone gets it! 🤝",
                    "Couldn't have said it better myself! 👏"
                ],
                'neutral': [
                    "Fair point! But let me play devil's advocate... 🎭",
                    "Interesting take! Here's a different angle... 🔄",
                    "I see where you're coming from! However... 🤔",
                    "Not bad! But wait till you hear this... 😏"
                ],
                'question': [
                    "Oh, good question! *cracks knuckles* Let's dive in... 🤓",
                    "Plot twist: I actually have an answer for this! 🎬",
                    "You had to ask the hard one, didn't you? 😅 Here goes...",
                    "Finally, someone asking the real questions! 🎯"
                ]
            },
            'professional': {
                'positive': [
                    "Thank you for your thoughtful feedback. I appreciate your support.",
                    "I'm grateful for your engagement on this topic.",
                    "Your insight adds significant value to this discussion.",
                    "Thank you for contributing to this professional dialogue."
                ],
                'neutral': [
                    "Thank you for sharing your perspective. It's valuable to consider different viewpoints.",
                    "I appreciate your input. This is an important aspect to discuss.",
                    "Your point is well-taken. Here's an additional consideration...",
                    "Thank you for raising this. Professional discourse benefits from such exchanges."
                ],
                'question': [
                    "Thank you for your question. Allow me to provide some clarity...",
                    "That's an excellent inquiry. Based on my experience...",
                    "I appreciate your thoughtful question. Here's my professional perspective...",
                    "Thank you for seeking deeper understanding. Let me explain..."
                ]
            }
        }
        
        # Response modifiers for different comment types
        self.comment_modifiers = {
            'compliment': [
                "Your support means a lot! 🎯",
                "Really appreciate you saying that! 💫",
                "You just made my day! 😊"
            ],
            'criticism': [
                "That's a fair point! I'll definitely consider that for next time. 🙏",
                "Thanks for the honest feedback - it helps me improve! 📈",
                "I hear you! Always looking to do better. 💪"
            ],
            'question': [
                "Hope that answers your question! Let me know if you'd like more details. 📚",
                "Does that help clarify? Happy to dive deeper! 🔍",
                "Great question! Would you like me to elaborate more? 💭"
            ],
            'agreement': [
                "Love that we're on the same page! 🤝",
                "Great minds think alike! 🧠",
                "Exactly! Thanks for backing that up! ✨"
            ]
        }
    
    def generate_reply(self, comment: str, tone: str = "friendly", 
                      context: str = "") -> str:
        """
        Generate an appropriate reply to a comment
        
        Args:
            comment: The comment or message to reply to
            tone: friendly, witty, or professional
            context: Additional context about the post/thread
        
        Returns:
            Generated reply string
        """
        
        # Determine comment type based on content
        comment_lower = comment.lower()
        comment_type = self._classify_comment(comment_lower)
        
        # Get appropriate template
        templates = self.reply_templates.get(tone, self.reply_templates['friendly'])
        type_templates = templates.get(comment_type, templates['neutral'])
        
        # Select random template
        base_reply = random.choice(type_templates)
        
        # Add modifier if appropriate
        if comment_type in self.comment_modifiers and random.random() > 0.6:
            modifier = random.choice(self.comment_modifiers[comment_type])
            base_reply += f" {modifier}"
        
        # Add context-specific personalization if provided
        if context and random.random() > 0.7:
            base_reply += f" Regarding {context[:50]}..."
        
        return base_reply
    
    def _classify_comment(self, comment: str) -> str:
        """Classify the comment type based on keywords and patterns"""
        
        # Check for questions
        if any(word in comment for word in ['?', 'what', 'how', 'why', 'when', 'who', 'which']):
            return 'question'
        
        # Check for compliments
        if any(word in comment for word in ['great', 'awesome', 'love', 'amazing', 'perfect', 'nice', 'good', 'thanks', 'thank']):
            return 'positive'
        
        # Check for agreement
        if any(word in comment for word in ['agree', 'same', 'exactly', 'true', 'right', 'yes']):
            return 'agreement'
        
        # Check for criticism
        if any(word in comment for word in ['but', 'however', 'actually', 'disagree', 'wrong', 'issue', 'problem']):
            return 'criticism'
        
        # Default to neutral
        return 'neutral'
    
    def generate_bulk_replies(self, comments: List[str], tone: str = "friendly") -> List[Dict]:
        """
        Generate replies for multiple comments
        
        Args:
            comments: List of comments to reply to
            tone: Tone to use for all replies
        
        Returns:
            List of dictionaries with original comment and generated reply
        """
        replies = []
        for comment in comments:
            reply = self.generate_reply(comment, tone)
            replies.append({
                'original_comment': comment,
                'generated_reply': reply,
                'tone': tone
            })
        return replies