#!/usr/bin/env python3
"""
Interactive Group Chat Renderer for GitHub Profile
Transforms GitHub Issue comments into mobile group chat interface
"""

import os
import re
import requests
import json
import time
import logging
from datetime import datetime, timezone
from dateutil import parser as date_parser
from urllib.parse import urlparse
import textwrap
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ChatConfig:
    """Configuration class for chat styling and behavior"""
    def __init__(self):
        self.chat_width = int(os.environ.get('CHAT_WIDTH', '50'))
        self.bubble_width = int(os.environ.get('BUBBLE_WIDTH', '38'))
        self.max_messages = int(os.environ.get('MAX_MESSAGES', '10'))
        self.chat_title = os.environ.get('CHAT_TITLE', '#builders-chat')
        self.enable_reactions = os.environ.get('ENABLE_REACTIONS', 'true').lower() == 'true'
        self.filter_bots = os.environ.get('FILTER_BOTS', 'true').lower() == 'true'
        self.max_retries = int(os.environ.get('MAX_RETRIES', '3'))
        self.retry_delay = float(os.environ.get('RETRY_DELAY', '1.0'))

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
                'body': "Any plans for CISSP study groups? 🛡️",
                'created_at': '2024-07-22T12:15:00Z',
                'author_association': 'NONE'
            },
            {
                'user': {'login': 'charlie_ml', 'type': 'User'},
                'body': "The Planify concept is brilliant! Putting money on the line really changes behavior 💰",
                'created_at': '2024-07-22T14:32:00Z',
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
    
    def wrap_message(self, text: str, width: int) -> List[str]:
        """Enhanced message wrapping with better URL and code handling"""
        if not text or not text.strip():
            return ['(empty message)']
        
        # Clean up the text
        text = text.strip()
        
        # Handle different content types
        if self._contains_code_block(text):
            return self._wrap_code_block(text, width)
        elif self._contains_urls(text):
            return self._wrap_with_urls(text, width)
        else:
            # Regular text wrapping with improved handling
            try:
                lines = textwrap.wrap(
                    text, 
                    width=width, 
                    break_long_words=False, 
                    break_on_hyphens=False,
                    expand_tabs=False
                )
                return lines if lines else [text[:width]]
            except Exception as e:
                logger.warning(f"Text wrapping failed: {e}")
                return [text[:width]]
    
    def _contains_code_block(self, text: str) -> bool:
        """Check if text contains code blocks"""
        return '```' in text or text.count('`') >= 2
    
    def _contains_urls(self, text: str) -> bool:
        """Check if text contains URLs"""
        return 'http://' in text or 'https://' in text or 'www.' in text
    
    def _wrap_code_block(self, text: str, width: int) -> List[str]:
        """Handle code block wrapping"""
        if '```' in text:
            # Multi-line code block - preserve formatting
            return [line[:width] for line in text.split('\n')]
        else:
            # Inline code - simple wrapping
            return self._wrap_with_special_content(text, width)
    
    def _wrap_with_urls(self, text: str, width: int) -> List[str]:
        """Wrap text containing URLs without breaking them"""
        return self._wrap_with_special_content(text, width)
    
    def _wrap_with_special_content(self, text: str, width: int) -> List[str]:
        """Wrap text with special content (URLs, code) without breaking"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= width:
                current_line.append(word)
                current_length += word_length + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text[:width]]
    
    def create_message_bubble(self, username: str, message: str, timestamp: str, is_owner: bool = False) -> List[str]:
        """Create an enhanced chat bubble with better formatting"""
        lines = []
        
        # Adjust bubble width based on content
        content_width = min(len(message), self.config.bubble_width - 4)
        bubble_width = max(content_width + 4, 20)  # Minimum bubble width
        
        wrapped_text = self.wrap_message(message, bubble_width - 4)
        
        # Add user status indicator
        status_indicator = "🔵" if is_owner else "⚪"
        
        if is_owner:
            # Right-aligned (your messages) with enhanced styling
            time_header = f"{timestamp} {username} {status_indicator}"
            lines.append(f"│{time_header:>{self.config.chat_width-2}}│")
            
            # Enhanced message bubble with rounded corners effect
            padding = self.config.chat_width - bubble_width - 2
            for i, line in enumerate(wrapped_text):
                if i == 0:
                    # Top of bubble with rounded effect
                    lines.append(f"│{'':<{padding}}╭{'─' * (bubble_width-2)}╮│")
                # Content with proper padding
                content = f"│ {line:<{bubble_width-4}} │"
                lines.append(f"│{'':<{padding}}{content}│")
            # Bottom of bubble
            lines.append(f"│{'':<{padding}}╰{'─' * (bubble_width-2)}╯│")
        else:
            # Left-aligned (others' messages) with enhanced styling
            time_header = f"{status_indicator} {username} {timestamp}"
            lines.append(f"│ {time_header:<{self.config.chat_width-3}}│")
            
            # Enhanced message bubble
            for i, line in enumerate(wrapped_text):
                if i == 0:
                    # Top of bubble with rounded effect
                    lines.append(f"│ ╭{'─' * (bubble_width-2)}╮{'':<{self.config.chat_width-bubble_width-3}}│")
                # Content with proper padding
                content = f"│ {line:<{bubble_width-4}} │"
                lines.append(f"│ {content}{'':<{self.config.chat_width-bubble_width-3}}│")
            # Bottom of bubble
            lines.append(f"│ ╰{'─' * (bubble_width-2)}╯{'':<{self.config.chat_width-bubble_width-3}}│")
        
        return lines
    
    def render_chat_interface(self, comments: List[Dict[str, Any]]) -> str:
        """Render the complete enhanced group chat interface"""
        chat_lines = []
        
        # Enhanced chat header with activity indicators
        header = f"💬 {self.config.chat_title}"
        participant_count = len(set(c['user']['login'] for c in comments))
        status = f"🟢 {participant_count} participants online"
        
        # Dynamic header with better styling
        chat_lines.extend([
            f"╭{'─' * (self.config.chat_width-2)}╮",
            f"│ {header:<{self.config.chat_width-4}} │",
            f"│ {status:<{self.config.chat_width-4}} │",
            f"├{'─' * (self.config.chat_width-2)}┤"
        ])
        
        # Handle empty chat state
        if not comments:
            empty_msg = "No messages yet... be the first to say hi! 👋"
            padding = (self.config.chat_width - len(empty_msg) - 4) // 2
            chat_lines.extend([
                f"│{'':<{self.config.chat_width-2}}│",
                f"│{' ' * padding}{empty_msg}{' ' * (self.config.chat_width - len(empty_msg) - padding - 2)}│",
                f"│{'':<{self.config.chat_width-2}}│"
            ])
        else:
            # Process recent comments with smarter limiting
            recent_comments = self._get_recent_comments(comments)
            
            for i, comment in enumerate(recent_comments):
                try:
                    username = comment['user']['login']
                    message = self._sanitize_message(comment['body'])
                    timestamp = self.format_timestamp(comment['created_at'])
                    is_owner = self._is_owner_comment(comment)
                    
                    # Add spacing between messages
                    if i > 0:
                        chat_lines.append(f"│{'':<{self.config.chat_width-2}}│")
                    
                    # Create enhanced message bubble
                    bubble_lines = self.create_message_bubble(username, message, timestamp, is_owner)
                    chat_lines.extend(bubble_lines)
                    
                except KeyError as e:
                    logger.warning(f"Skipping malformed comment: missing {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing comment: {e}")
                    continue
        
        # Enhanced footer with better engagement prompt
        issue_link = f"Issue #{self.issue_number}"
        join_msg = "💭 Join the conversation at"
        chat_lines.extend([
            f"│{'':<{self.config.chat_width-2}}│",
            f"├{'─' * (self.config.chat_width-2)}┤",
            f"│ {join_msg} {issue_link:<{self.config.chat_width-len(join_msg)-4}} │",
            f"╰{'─' * (self.config.chat_width-2)}╯"
        ])
        
        return '\n'.join(chat_lines)
    
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