#!/usr/bin/env python3
"""
Interactive Group Chat Renderer for GitHub Profile
Transforms GitHub Issue comments into modern HTML chat interface
Powered by HTML engine with CSS styling and responsive design
"""

import os
import re
import requests
import time
import logging
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional, Any, Union
from functools import lru_cache

# Import HTML-powered chat engine
from html_engine import create_html_chat_interface, HtmlChatConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ChatConfig:
    """Configuration class for chat styling and behavior with validation."""
    def __init__(self):
        # Load and validate environment variables
        self.chat_width = self._get_positive_int('CHAT_WIDTH', 80)
        self.max_messages = self._get_positive_int('MAX_MESSAGES', 10)
        self.chat_title = os.environ.get('CHAT_TITLE', '#readme-chat').strip()
        self.enable_reactions = self._get_bool('ENABLE_REACTIONS', True)
        self.filter_bots = self._get_bool('FILTER_BOTS', True)
        self.max_retries = self._get_positive_int('MAX_RETRIES', 3)
        self.retry_delay = self._get_positive_float('RETRY_DELAY', 1.0)
      
        # Engine configuration with validation
        max_lines = self._get_positive_int('MAX_LINES_PER_MESSAGE', 6)
        self.max_lines_per_message = max_lines
        self.html_config = HtmlChatConfig(
            max_width=os.environ.get('CHAT_MAX_WIDTH', '600px'),
            theme=os.environ.get('CHAT_THEME', 'github'),
            show_timestamps=self._get_bool('SHOW_TIMESTAMPS', True),
            max_lines_per_message=max_lines,
            enable_avatars=self._get_bool('ENABLE_AVATARS', False),
            enable_reactions=self._get_bool('ENABLE_REACTIONS', False),
            human_friendly_time=self._get_bool('HUMAN_FRIENDLY_TIME', False),
            avatar_size=os.environ.get('AVATAR_SIZE', '32px')
        )
  
    def _get_positive_int(self, var_name: str, default: int) -> int:
        """Get positive integer from environment with validation."""
        try:
            value = int(os.environ.get(var_name, str(default)))
            return max(1, value)  # Ensure positive
        except (ValueError, TypeError):
            logger.warning(f"Invalid {var_name}, using default: {default}")
            return default
  
    def _get_positive_float(self, var_name: str, default: float) -> float:
        """Get positive float from environment with validation."""
        try:
            value = float(os.environ.get(var_name, str(default)))
            return max(0.1, value)  # Ensure positive
        except (ValueError, TypeError):
            logger.warning(f"Invalid {var_name}, using default: {default}")
            return default
  
    def _get_bool(self, var_name: str, default: bool) -> bool:
        """Get boolean from environment with validation."""
        try:
            value = os.environ.get(var_name, str(default)).lower()
            return value in ('true', '1', 'yes', 'on', 'enabled')
        except (ValueError, TypeError, AttributeError):
            logger.warning(f"Invalid {var_name}, using default: {default}")
            return default

class GroupChatRenderer:
    def __init__(self):
        # Validate required environment variables
        self.github_token = self._get_required_env('GITHUB_TOKEN')
        self.repo_owner = self._get_required_env('REPO_OWNER')
        self.repo_name = self._get_required_env('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER', '2')  # Change default to Issue #2
      
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
        """Get required environment variable with enhanced validation.
      
        Args:
            var_name: Environment variable name
          
        Returns:
            Environment variable value
          
        Raises:
            ValueError: If required variable is missing
        """
        value = os.environ.get(var_name, '').strip()
        if not value and var_name == 'GITHUB_TOKEN':
            logger.warning(f"Missing {var_name}, will use mock data for testing")
            return ''
        elif not value:
            raise ValueError(f"Required environment variable {var_name} is not set")
      
        # Additional validation for specific variables
        if var_name in ['REPO_OWNER', 'REPO_NAME']:
            if not self._is_valid_github_identifier(value):
                raise ValueError(f"Invalid {var_name} format: {value}")
              
        return value
      
    def _is_valid_github_identifier(self, identifier: str) -> bool:
        """Validate GitHub username/repository name format."""
        import re
        # GitHub usernames and repo names: alphanumeric, hyphens, underscores
        pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        return bool(pattern.match(identifier) and 1 <= len(identifier) <= 39)
      
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
                'user': {'login': self.repo_owner, 'type': 'User'},
                'body': "Thanks! The facial recognition is hitting 94% accuracy now. Still tuning the vocal cues...",
                'created_at': '2024-07-22T11:47:00Z',
                'author_association': 'OWNER',
                'reactions': {
                    '+1': 3,
                    'rocket': 2,
                    'eyes': 1
                }
            },
            {
                'user': {'login': 'bob_sec', 'type': 'User'},
                'body': "Any plans for CISSP study groups?",
                'created_at': '2024-07-22T12:15:00Z',
                'author_association': 'NONE',
                'reactions': {
                    '+1': 1,
                    'heart': 2
                }
            },
            {
                'user': {'login': 'charlie_ml', 'type': 'User'},
                'body': "This is absolutely fascinating! I've been diving deep into your LookbackAI project and the technical implementation is genuinely impressive. The facial recognition accuracy you mentioned (94%) is remarkable for real-time processing. I'm particularly curious about how you're handling edge cases with varying lighting conditions and different facial angles. The vocal cue analysis component sounds like an innovative approach to emotion detection. Have you considered implementing ensemble methods to combine multiple neural networks for even better accuracy? Also, the integration with video journaling is brilliant - it creates a feedback loop that could really help users understand their emotional patterns over time. This kind of self-awareness tooling could be transformative for mental health applications.",
                'created_at': '2024-07-22T14:32:00Z',
                'author_association': 'NONE',
                'reactions': {
                    '+1': 5,
                    'hooray': 1,
                    'rocket': 3,
                    'heart': 2
                }
            },
            {
                'user': {'login': 'david_devops', 'type': 'User'},
                'body': "Quick question about deployment! Looking at Docker + Kubernetes for production. Any thoughts on scaling strategies?",
                'created_at': '2024-07-22T15:45:00Z',
                'author_association': 'NONE',
                'reactions': {
                    '+1': 2,
                    'eyes': 4
                }
            }
        ]
  
  
    def render_chat_interface(self, comments: List[Dict[str, Any]]) -> str:
        """Render chat interface using HTML engine"""
        # Process comments for HTML engine
        processed_comments = []
        recent_comments = self._get_recent_comments(comments)
      
        for comment in recent_comments:
            try:
                processed_comment = {
                    'user': {'login': comment['user']['login']},
                    'body': self._sanitize_message(comment['body']),
                    'created_at': comment['created_at'],
                    'author_association': comment.get('author_association', 'NONE'),
                    'is_owner': self._is_owner_comment(comment),  # Pre-compute owner status
                    'reactions': comment.get('reactions', {})  # Include reactions if available
                }
                processed_comments.append(processed_comment)
            except (KeyError, Exception) as e:
                logger.warning(f"Skipping malformed comment: {e}")
                continue
      
        # Use HTML-powered engine for rendering
        return create_html_chat_interface(
            processed_comments,
            config=self.config.html_config,
            title=self.config.chat_title,
            issue_number=self.issue_number
        )
  
    def _get_recent_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get recent comments with smart pagination"""
        if len(comments) <= self.config.max_messages:
            return comments
      
        # Show most recent comments but ensure conversation flow
        return comments[-self.config.max_messages:]
  
    @lru_cache(maxsize=128)
    def _sanitize_message(self, message: str) -> str:
        """Sanitize message content for display with caching.
      
        Args:
            message: Raw message content
          
        Returns:
            Sanitized message content
        """
        if not message or not message.strip():
            return "(empty message)"
      
        try:
            # Normalize whitespace and strip
            sanitized = ' '.join(message.strip().split())
          
            # Truncate very long messages with word boundary awareness
            max_length = self.config.max_message_length if hasattr(self.config, 'max_message_length') else 500
            if len(sanitized) > max_length:
                # Find last word boundary before max_length
                truncate_pos = sanitized.rfind(' ', 0, max_length - 3)
                if truncate_pos > max_length // 2:  # Reasonable word boundary found
                    sanitized = sanitized[:truncate_pos] + "..."
                else:  # No good word boundary, hard truncate
                    sanitized = sanitized[:max_length-3] + "..."
          
            return sanitized
          
        except Exception as e:
            logger.warning(f"Message sanitization failed: {e}")
            return "[Message formatting error]"
  
    @lru_cache(maxsize=64)
    def _is_owner_comment_cached(self, username: str, author_association: str) -> bool:
        """Cached check for owner comment status."""
        return (author_association == 'OWNER' or username == self.repo_owner)
      
    def _is_owner_comment(self, comment: Dict[str, Any]) -> bool:
        """Check if comment is from repository owner with enhanced validation.
      
        Args:
            comment: Comment dictionary from GitHub API
          
        Returns:
            True if comment is from repository owner
        """
        try:
            username = comment.get('user', {}).get('login', '')
            author_association = comment.get('author_association', 'NONE')
            return self._is_owner_comment_cached(username, author_association)
        except (KeyError, AttributeError, TypeError) as e:
            logger.warning(f"Error checking comment ownership: {e}")
            return False
  
    def update_readme(self, chat_content: str):
        """Update an SVG file with the rendered chat content."""
        svg_path = 'chat-display.svg'
        logger.info("Using SVG path: " + svg_path)
        # The SVG wrapper with the <foreignObject> tag
        # We must define the dimensions of the SVG here
        svg_template = f"""
    <svg fill="none" width="650" height="500" xmlns="http://www.w3.org/2000/svg">
        <foreignObject width="100%" height="100%">
            <div xmlns="http://www.w3.org/1999/xhtml">
                {chat_content}
            </div>
        </foreignObject>
    </svg>
    """
        
        try:
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_template.strip())
            print(f"✅ SVG file updated at {svg_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing SVG file: {e}")
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