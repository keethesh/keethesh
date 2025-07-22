#!/usr/bin/env python3
"""
Rich-Powered ASCII Engine for Chat Interfaces
Combines Rich's Unicode robustness with chat-specific domain logic

Public API:
    create_chat_interface() - Main function to render complete chat interface
    
Internal implementation uses Rich library for robust Unicode handling.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Sequence
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
import re
from wcwidth import wcswidth

def visual_width(text: str) -> int:
    """Return how many columns the text occupies in terminal display"""
    width = wcswidth(text)
    # Handle unassigned code points (wcwidth returns None for some characters)
    return width if width is not None else len(text)

def ljust_visual(text: str, width: int) -> str:
    """Left-justify text based on visual width, not character count"""
    current_width = visual_width(text)
    padding = max(width - current_width, 0)
    return f"{text}{' ' * padding}"


# Private classes for internal engine use only
@dataclass(slots=True)
class _ChatCanvas:
    """Internal chat interface canvas"""
    width: int = 80
    title: str = "#readme-chat"
    
    def create_header(self, participant_count: int) -> List[str]:
        """Create detailed terminal window interface"""
        # Terminal window controls and title bar
        controls = "[_] [^] [X]"  # ASCII window controls
        title_text = f"Terminal - {self.title}"
        
        # Calculate spacing for centered title with controls
        total_controls_width = len(controls) + 2  # controls + padding
        available_for_title = self.width - total_controls_width - 2  # -2 for borders
        title_padding = max(0, available_for_title - len(title_text))
        left_pad = title_padding // 2
        right_pad = title_padding - left_pad
        
        title_bar = f"{controls}  {' ' * left_pad}{title_text}{' ' * right_pad}"
        title_bar_padding = max(0, self.width - len(title_bar) - 2)
        
        # System information line with scrollback indicator
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        system_info = f"Last activity: {current_time} | Shell: /bin/bash | Users: {participant_count} | [Scroll: ^^^]"
        system_padding = max(0, self.width - len(system_info))
        
        # Main terminal prompt with git branch indicator
        git_branch = "(main)"  # Simulate git branch
        header_line = f"keethesh@github:~/{self.title.replace('#', '')} {git_branch}$ # Connected to live chat"
        header_width = visual_width(header_line)
        header_padding = max(0, self.width - header_width)
        
        return [
            f"+{'-' * (self.width-2)}+",
            f"|{title_bar}{' ' * title_bar_padding}|",
            f"|{system_info}{' ' * system_padding}|",
            f"+{'-' * (self.width-2)}+",
            f"{header_line}{' ' * header_padding}"
        ]
    
    def create_footer(self, issue_number: str) -> List[str]:
        """Create detailed terminal footer with connection info"""
        # Terminal status information
        status_line = f"--- Terminal Session Active --- Press Ctrl+C to exit --- Connected to Issue #{issue_number} ---"
        status_padding = max(0, self.width - len(status_line))
        
        # Join command prompt
        join_line = f"keethesh@github:~/readme-chat (main)$ echo 'Join the conversation at github.com/keethesh/keethesh/issues/{issue_number}'"
        join_width = visual_width(join_line)
        join_padding = max(0, self.width - join_width)
        
        # Terminal cursor indicator
        cursor_line = f"keethesh@github:~/readme-chat (main)$ _"
        cursor_padding = max(0, self.width - len(cursor_line))
        
        return [
            f"{status_line}{' ' * status_padding}",
            f"{join_line}{' ' * join_padding}",
            f"{cursor_line}{' ' * cursor_padding}",
            f"+{'-' * (self.width-2)}+"
        ]
    
    def create_spacer(self) -> List[str]:
        """Create empty spacer line"""
        return [f"{' ' * self.width}"]


# Internal convenience function
def _create_message_bubble(content: str, username: str, timestamp: str, 
                          is_owner: bool = False, chat_width: int = 80,
                          max_lines: int = 4, issue_number: str = "1") -> List[str]:
    """Create terminal-style message lines"""
    import textwrap
    
    # Enhanced terminal prompt style with timestamps and indicators
    import datetime
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    if is_owner:
        # Owner gets repo context and special indicator
        prompt = f"[{current_time}] {username}@github:~/readme-chat (main)$ # "
    else:
        # Visitors get general prompt
        prompt = f"[{current_time}] {username}@github:~$ # "
    
    # Calculate available width for content
    prompt_width = visual_width(prompt)
    available_width = chat_width - prompt_width
    
    # Wrap content to fit available width
    wrapped_lines = []
    for paragraph in content.split('\n'):
        if paragraph.strip():
            paragraph_lines = textwrap.wrap(
                paragraph.strip(), 
                width=available_width,
                break_long_words=True,
                break_on_hyphens=True
            )
            wrapped_lines.extend(paragraph_lines)
        else:
            wrapped_lines.append('')
    
    # Apply smart truncation with typing indicator
    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[:max_lines-1]
        wrapped_lines.append(f"[... see more at Issue #{issue_number}] <typing...>")
    
    result = []
    
    # First line with full prompt
    if wrapped_lines:
        first_line = wrapped_lines[0]
        line = f"{prompt}{first_line}"
        # Pad to exact width
        padding = max(0, chat_width - visual_width(line))
        result.append(f"{line}{' ' * padding}")
        
        # Continuation lines with shell-style continuation
        continuation_prompt = ">" + " " * (prompt_width - 1)  # Shell continuation indicator
        for i, line in enumerate(wrapped_lines[1:], 1):
            continued_line = f"{continuation_prompt}{line}"
            # Add cursor indicator to final line
            if i == len(wrapped_lines) - 1 and not line.startswith("[..."):
                continued_line += " |"  # Cursor indicator
            padding = max(0, chat_width - visual_width(continued_line))
            result.append(f"{continued_line}{' ' * padding}")
    else:
        # Empty message
        padding = max(0, chat_width - prompt_width)
        result.append(f"{prompt}{' ' * padding}")
    
    return result


def create_chat_interface(comments: List[dict], chat_width: int = 80, 
                         title: str = "#readme-chat", issue_number: str = "1", 
                         max_lines: int = 4) -> str:
    """Create complete chat interface using Rich-powered engine"""
    canvas = _ChatCanvas(width=chat_width, title=title)
    
    # Build chat interface
    lines = []
    
    # Header
    participant_count = len(set(c['user']['login'] for c in comments))
    lines.extend(canvas.create_header(participant_count))
    
    # Messages
    for i, comment in enumerate(comments):        
        username = comment['user']['login']
        content = comment['body']
        timestamp = comment.get('created_at', '')
        is_owner = comment.get('is_owner', False)  # Use pre-computed owner status
        
        # Format timestamp (simplified) - not used in terminal format but kept for compatibility
        if timestamp:
            try:
                from dateutil import parser as date_parser
                dt = date_parser.parse(timestamp)
                formatted_time = dt.strftime('%H:%M')
            except:
                formatted_time = '??:??'
        else:
            formatted_time = '??:??'
        
        message_lines = _create_message_bubble(
            content, username, formatted_time, is_owner, 
            chat_width, max_lines=max_lines, issue_number=issue_number
        )
        lines.extend(message_lines)
    
    # Footer
    lines.extend(canvas.create_footer(issue_number))
    
    return '\n'.join(lines)