#!/usr/bin/env python3
"""
Interactive Group Chat Renderer for GitHub Profile
Transforms GitHub Issue comments into mobile group chat interface
"""

import os
import re
import requests
import json
from datetime import datetime
from dateutil import parser as date_parser
import textwrap

class GroupChatRenderer:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo_owner = os.environ.get('REPO_OWNER')
        self.repo_name = os.environ.get('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER', '1')
        
        # Chat styling configuration
        self.chat_width = 45
        self.bubble_width = 35
        self.max_messages = 8  # Keep chat scrollable
        
    def fetch_issue_comments(self):
        """Fetch comments from the featured GitHub issue"""
        if not self.github_token:
            print("No GitHub token provided, using mock data")
            return self._get_mock_data()
            
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}/comments"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return self._get_mock_data()
    
    def _get_mock_data(self):
        """Provide mock data for testing"""
        return [
            {
                'user': {'login': 'alice_dev'},
                'body': "Hey! Love your LookbackAI project. How's the AI model performing?",
                'created_at': '2024-07-22T10:23:00Z',
                'author_association': 'NONE'
            },
            {
                'user': {'login': self.repo_owner},
                'body': "Thanks! The facial recognition is hitting 94% accuracy now. Still tuning the vocal cues...",
                'created_at': '2024-07-22T11:47:00Z',
                'author_association': 'OWNER'
            },
            {
                'user': {'login': 'bob_sec'},
                'body': "Any plans for CISSP study groups? 🛡️",
                'created_at': '2024-07-22T12:15:00Z',
                'author_association': 'NONE'
            }
        ]
    
    def format_timestamp(self, timestamp_str):
        """Convert GitHub timestamp to chat-style time"""
        try:
            dt = date_parser.parse(timestamp_str)
            return dt.strftime('%H:%M')
        except:
            return '00:00'
    
    def wrap_message(self, text, width):
        """Smart word wrapping for chat bubbles"""
        # Handle URLs and code snippets specially
        if 'http' in text or '`' in text:
            # Simple wrapping for special content
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= width:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            return lines
        
        # Regular text wrapping
        return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    
    def create_message_bubble(self, username, message, timestamp, is_owner=False):
        """Create a chat bubble for a message"""
        lines = []
        wrapped_text = self.wrap_message(message, self.bubble_width - 4)
        
        if is_owner:
            # Right-aligned (your messages)
            time_header = f"{timestamp} {username}"
            lines.append(f"│{time_header:>{self.chat_width-2}}│")
            
            # Message bubble
            for i, line in enumerate(wrapped_text):
                if i == 0:
                    lines.append(f"│{'':<{self.chat_width-self.bubble_width-2}}┌{'─' * (self.bubble_width-2)}┐│")
                content = f"│ {line} │"
                lines.append(f"│{'':<{self.chat_width-self.bubble_width-2}}{content:<{self.bubble_width}}│")
            lines.append(f"│{'':<{self.chat_width-self.bubble_width-2}}└{'─' * (self.bubble_width-2)}┘│")
        else:
            # Left-aligned (others' messages)
            time_header = f"{username} {timestamp}"
            lines.append(f"│ {time_header:<{self.chat_width-3}}│")
            
            # Message bubble
            for i, line in enumerate(wrapped_text):
                if i == 0:
                    lines.append(f"│ ┌{'─' * (self.bubble_width-2)}┐{'':<{self.chat_width-self.bubble_width-2}}│")
                content = f"│ {line} │"
                lines.append(f"│ {content:<{self.bubble_width}}{'':<{self.chat_width-self.bubble_width-2}}│")
            lines.append(f"│ └{'─' * (self.bubble_width-2)}┘{'':<{self.chat_width-self.bubble_width-2}}│")
        
        return lines
    
    def render_chat_interface(self, comments):
        """Render the complete group chat interface"""
        chat_lines = []
        
        # Chat header
        header = "💬 #keethesh-chat"
        status = "🟢 community online"
        chat_lines.extend([
            f"┌{'─' * (self.chat_width-2)}┐",
            f"│ {header:<{self.chat_width-4}} │",
            f"│ {status:<{self.chat_width-4}} │",
            f"├{'─' * (self.chat_width-2)}┤"
        ])
        
        # Process recent comments (limit to max_messages)
        recent_comments = comments[-self.max_messages:] if len(comments) > self.max_messages else comments
        
        for i, comment in enumerate(recent_comments):
            username = comment['user']['login']
            message = comment['body']
            timestamp = self.format_timestamp(comment['created_at'])
            is_owner = comment.get('author_association') == 'OWNER' or username == self.repo_owner
            
            # Add spacing between messages
            if i > 0:
                chat_lines.append(f"│{'':<{self.chat_width-2}}│")
            
            # Create message bubble
            bubble_lines = self.create_message_bubble(username, message, timestamp, is_owner)
            chat_lines.extend(bubble_lines)
        
        # Chat footer with engagement prompt
        chat_lines.extend([
            f"│{'':<{self.chat_width-2}}│",
            f"├{'─' * (self.chat_width-2)}┤",
            f"│ 💭 Join the conversation at Issue #{self.issue_number:<{self.chat_width-33}} │",
            f"└{'─' * (self.chat_width-2)}┘"
        ])
        
        return '\n'.join(chat_lines)
    
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
    """Main execution function"""
    print("🚀 Starting group chat renderer...")
    
    renderer = GroupChatRenderer()
    
    # Fetch and process comments
    print(f"📡 Fetching comments from issue #{renderer.issue_number}...")
    comments = renderer.fetch_issue_comments()
    
    if not comments:
        print("No comments found, using empty chat")
        comments = []
    
    print(f"💬 Processing {len(comments)} comments...")
    
    # Render chat interface
    chat_content = renderer.render_chat_interface(comments)
    
    # Update README
    success = renderer.update_readme(chat_content)
    
    if success:
        print("✨ Group chat interface updated successfully!")
    else:
        print("❌ Failed to update README")
        exit(1)

if __name__ == "__main__":
    main()