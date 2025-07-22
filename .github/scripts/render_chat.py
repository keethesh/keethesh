#!/usr/bin/env python3
"""
Interactive Group Chat Renderer for GitHub Profile
Transforms GitHub Issue comments into mobile group chat interface
Powered by Rich-powered ASCII engine for robust Unicode handling
"""

import os
import re
import requests
import time
import logging
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional, Any

# Import Rich-powered ASCII engine
from ascii_engine import create_chat_interface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ChatConfig:
    """Configuration class for chat styling and behavior"""
    def __init__(self):
        self.chat_width = int(os.environ.get('CHAT_WIDTH', '50'))
        self.max_messages = int(os.environ.get('MAX_MESSAGES', '10'))
        self.chat_title = os.environ.get('CHAT_TITLE', '#builders-chat')
        self.enable_reactions = os.environ.get('ENABLE_REACTIONS', 'true').lower() == 'true'
        self.filter_bots = os.environ.get('FILTER_BOTS', 'true').lower() == 'true'
        self.max_retries = int(os.environ.get('MAX_RETRIES', '3'))
        self.retry_delay = float(os.environ.get('RETRY_DELAY', '1.0'))
        
        # Engine configuration (passed to ascii_engine)
        self.max_lines_per_message = int(os.environ.get('MAX_LINES_PER_MESSAGE', '4'))

class GroupChatRenderer:
    def __init__(self):
        # Validate required environment variables
        self.github_token = self._get_required_env('GITHUB_TOKEN')
        self.repo_owner = self._get_required_env('REPO_OWNER')
        self.repo_name = self._get_required_env('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER', '1')
        
        # Load configuration
        self.config = ChatConfig()
        
        # Initialize session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'{self.repo_owner}/{self.repo_name}-chat-bot'
        })
        
        logger.info(f"Initialized chat renderer for {self.repo_owner}/{self.repo_name} issue #{self.issue_number}")
    
    def _get_required_env(self, var_name: str) -> str:
        """Get required environment variable with validation"""
        value = os.environ.get(var_name)
        if not value and var_name == 'GITHUB_TOKEN':
            logger.warning(f"Missing {var_name}, will use mock data for testing")
            return ''
        elif not value:
            raise ValueError(f"Required environment variable {var_name} is not set")
        return value
        
    def fetch_issue_comments(self) -> List[Dict[str, Any]]:
        """Fetch comments from the featured GitHub issue with retry logic"""
        if not self.github_token:
            logger.warning("No GitHub token provided, using mock data")
            return self._get_mock_data()
            
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}/comments"
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Fetching comments (attempt {attempt + 1}/{self.config.max_retries})")
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 403:
                    logger.error("API rate limit exceeded or insufficient permissions")
                    if 'X-RateLimit-Reset' in response.headers:
                        reset_time = int(response.headers['X-RateLimit-Reset'])
                        logger.info(f"Rate limit resets at {datetime.fromtimestamp(reset_time)}")
                    return self._get_mock_data()
                
                response.raise_for_status()
                comments = response.json()
                
                # Filter out bot comments if enabled
                if self.config.filter_bots:
                    comments = [c for c in comments if not self._is_bot_comment(c)]
                
                logger.info(f"Successfully fetched {len(comments)} comments")
                return comments
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All {self.config.max_retries} attempts failed, using mock data")
                    return self._get_mock_data()
            
            except Exception as e:
                logger.error(f"Unexpected error fetching comments: {e}")
                return self._get_mock_data()
    
    def _is_bot_comment(self, comment: Dict[str, Any]) -> bool:
        """Check if comment is from a bot account"""
        user = comment.get('user', {})
        user_type = user.get('type', '').lower()
        username = user.get('login', '').lower()
        
        # Common bot indicators
        bot_indicators = ['bot', 'github-actions', 'dependabot', 'renovate']
        return (user_type == 'bot' or 
                any(indicator in username for indicator in bot_indicators))
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """Provide enhanced mock data for testing"""
        return [
            {
                'user': {'login': 'alice_dev', 'type': 'User'},
                'body': "Hey! Love your LookbackAI project. How's the AI model performing?",
                'created_at': '2024-07-22T10:23:00Z',
                'author_association': 'NONE'
            },
            {
                'user': {'login': self.repo_owner, 'type': 'User'},
                'body': "Thanks! The facial recognition is hitting 94% accuracy now. Still tuning the vocal cues...",
                'created_at': '2024-07-22T11:47:00Z',
                'author_association': 'OWNER'
            },
            {
                'user': {'login': 'bob_sec', 'type': 'User'},
                'body': "Any plans for CISSP study groups?",
                'created_at': '2024-07-22T12:15:00Z',
                'author_association': 'NONE'
            },
            {
                'user': {'login': 'charlie_ml', 'type': 'User'},
                'body': "This is absolutely fascinating! I've been diving deep into your LookbackAI project and the technical implementation is genuinely impressive. The facial recognition accuracy you mentioned (94%) is remarkable for real-time processing. I'm particularly curious about how you're handling edge cases with varying lighting conditions and different facial angles. The vocal cue analysis component sounds like an innovative approach to emotion detection. Have you considered implementing ensemble methods to combine multiple neural networks for even better accuracy? Also, the integration with video journaling is brilliant - it creates a feedback loop that could really help users understand their emotional patterns over time. This kind of self-awareness tooling could be transformative for mental health applications.",
                'created_at': '2024-07-22T14:32:00Z',
                'author_association': 'NONE'
            },
            {
                'user': {'login': 'david_devops', 'type': 'User'},
                'body': "Quick question about deployment! Looking at Docker + Kubernetes for production. Any thoughts on scaling strategies?",
                'created_at': '2024-07-22T15:45:00Z',
                'author_association': 'NONE'
            }
        ]
    
    def format_timestamp(self, timestamp_str: str) -> str:
        """Convert GitHub timestamp to chat-style time with better error handling"""
        try:
            dt = date_parser.parse(timestamp_str)
            # Convert to local timezone for better UX
            local_dt = dt.astimezone()
            return local_dt.strftime('%H:%M')
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return '??:??'
    
    
    def render_chat_interface(self, comments: List[Dict[str, Any]]) -> str:
        """Render chat interface using Rich-powered ASCII engine"""
        if not comments:
            # Let the engine handle empty state
            return create_chat_interface(
                [],
                chat_width=self.config.chat_width,
                title=self.config.chat_title,
                issue_number=self.issue_number,
                max_lines=self.config.max_lines_per_message
            )
        
        # Process comments for Rich engine
        processed_comments = []
        recent_comments = self._get_recent_comments(comments)
        
        for comment in recent_comments:
            try:
                processed_comment = {
                    'user': {'login': comment['user']['login']},
                    'body': self._sanitize_message(comment['body']),
                    'created_at': comment['created_at'],
                    'author_association': comment.get('author_association', 'NONE'),
                    'is_owner': self._is_owner_comment(comment)  # Pre-compute owner status
                }
                processed_comments.append(processed_comment)
            except (KeyError, Exception) as e:
                logger.warning(f"Skipping malformed comment: {e}")
                continue
        
        # Use Rich-powered engine for rendering
        return create_chat_interface(
            processed_comments,
            chat_width=self.config.chat_width,
            title=self.config.chat_title,
            issue_number=self.issue_number,
            max_lines=self.config.max_lines_per_message
        )
    
    def _get_recent_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get recent comments with smart pagination"""
        if len(comments) <= self.config.max_messages:
            return comments
        
        # Show most recent comments but ensure conversation flow
        return comments[-self.config.max_messages:]
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize message content for display"""
        if not message:
            return "(empty message)"
        
        # Basic sanitization
        sanitized = message.strip()
        
        # Truncate very long messages
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized
    
    def _is_owner_comment(self, comment: Dict[str, Any]) -> bool:
        """Check if comment is from repository owner"""
        return (comment.get('author_association') == 'OWNER' or 
                comment['user']['login'] == self.repo_owner)
    
    def update_readme(self, chat_content):
        """Update README.md with the rendered chat"""
        readme_path = 'README.md'
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print("README.md not found")
            return False
        
        # Define chat markers
        start_marker = "<!-- CHAT_START -->"
        end_marker = "<!-- CHAT_END -->"
        
        # Check if markers exist
        if start_marker not in content:
            # Add chat section to README
            chat_section = f"""
### 💬 Community Chat
Join the conversation! Comment on [Issue #{self.issue_number}](https://github.com/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}) to see your message appear here.

{start_marker}
```
{chat_content}
```
{end_marker}
"""
            # Insert before the "Latest Learnings" section
            til_pattern = r'(### 🧠 Latest Learnings)'
            if re.search(til_pattern, content):
                content = re.sub(til_pattern, chat_section + r'\n\1', content)
            else:
                # Append at the end if TIL section not found
                content += chat_section
        else:
            # Replace existing chat content
            pattern = f'{re.escape(start_marker)}.*?{re.escape(end_marker)}'
            replacement = f'{start_marker}\n```\n{chat_content}\n```\n{end_marker}'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write updated content
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ README updated with {len(chat_content.split(chr(10)))} lines of chat")
            return True
        except Exception as e:
            print(f"❌ Error writing README: {e}")
            return False

def main():
    """Enhanced main execution function with comprehensive error handling"""
    try:
        logger.info("🚀 Starting enhanced group chat renderer...")
        
        # Initialize renderer with validation
        renderer = GroupChatRenderer()
        
        # Display configuration for transparency
        logger.info(f"Configuration: width={renderer.config.chat_width}, "
                   f"max_messages={renderer.config.max_messages}, "
                   f"title='{renderer.config.chat_title}'")
        
        # Fetch and process comments with retries
        logger.info(f"📡 Fetching comments from issue #{renderer.issue_number}...")
        comments = renderer.fetch_issue_comments()
        
        logger.info(f"💬 Processing {len(comments)} comments...")
        
        # Render enhanced chat interface
        chat_content = renderer.render_chat_interface(comments)
        
        # Validate generated content
        if not chat_content or len(chat_content.strip()) == 0:
            logger.error("Generated chat content is empty")
            exit(1)
        
        # Update README with enhanced error handling
        success = renderer.update_readme(chat_content)
        
        if success:
            logger.info("✨ Group chat interface updated successfully!")
        else:
            logger.error("❌ Failed to update README")
            exit(1)
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug("Full traceback:", exc_info=True)
        exit(1)
    finally:
        # Cleanup
        if 'renderer' in locals() and hasattr(renderer, 'session'):
            renderer.session.close()
            logger.debug("HTTP session closed")

if __name__ == "__main__":
    main()