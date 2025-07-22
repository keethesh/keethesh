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
    width: int = 50
    title: str = "#builders-chat"
    
    def create_header(self, participant_count: int) -> List[str]:
        """Create professional terminal-style header"""
        # Manual header creation for precise control
        header_text = f"# {self.title}"
        status_text = f"({participant_count} online)"
        
        # Use visual width for accurate calculation
        header_width = visual_width(header_text)
        status_width = visual_width(status_text)
        available_space = self.width - header_width - status_width - 6
        separator = '·' * max(available_space, 1)
        
        header_line = f"│ {header_text} {separator} {status_text} │"
        
        return [
            f"╭{'─' * (self.width-2)}╮",
            header_line,
            f"├{'─' * (self.width-2)}┤"
        ]
    
    def create_footer(self, issue_number: str) -> List[str]:
        """Create engagement footer"""
        footer_text = f"Join the conversation at Issue #{issue_number}"
        # Use visual width for accurate calculation
        footer_width = visual_width(footer_text)
        footer_spaces = max(0, (self.width - 4) - footer_width)
        
        return [
            f"├{'─' * (self.width-2)}┤",
            f"│ {footer_text}{' ' * footer_spaces} │",
            f"╰{'─' * (self.width-2)}╯"
        ]
    
    def create_spacer(self) -> List[str]:
        """Create empty spacer line"""
        return [f"│{' ' * (self.width-2)}│"]


# Internal convenience function
def _create_message_bubble(content: str, username: str, timestamp: str, 
                          is_owner: bool = False, chat_width: int = 50,
                          max_lines: int = 4, issue_number: str = "1") -> List[str]:
    """Create a chat bubble with professional text wrapping and truncation"""
    import textwrap
    
    # Smart text wrapping with Unicode awareness
    max_content_width = 34  # Conservative width for bubble content
    
    # Wrap content intelligently
    wrapped_lines = []
    for paragraph in content.split('\n'):
        if paragraph.strip():
            paragraph_lines = textwrap.wrap(
                paragraph.strip(), 
                width=max_content_width,
                break_long_words=True,
                break_on_hyphens=True
            )
            wrapped_lines.extend(paragraph_lines)
        else:
            wrapped_lines.append('')  # Preserve empty lines
    
    # Apply smart truncation
    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[:max_lines-1]
        wrapped_lines.append(f"[... see full comment in Issue #{issue_number}]")
    
    # Calculate optimal bubble width based on visual width
    if wrapped_lines:
        max_visual_width = max(visual_width(line) for line in wrapped_lines)
        bubble_width = min(max_visual_width + 4, 38)
        bubble_width = max(bubble_width, 20)
    else:
        bubble_width = 20
    
    result = []
    
    if is_owner:
        # Right-aligned owner messages
        header = f"{timestamp} {username} (OP)"
        # Use visual width for accurate calculation
        header_width = visual_width(header)
        padding = max(0, chat_width - header_width - 2)  # -2 for borders
        result.append(f"│{' ' * padding}{header}│")
        
        # Bubble with proper alignment
        bubble_padding = chat_width - bubble_width - 3  # Account for outer borders + 1 space
        result.append(f"│{' ' * bubble_padding}╭{'─' * (bubble_width-2)}╮ │")
        for line in wrapped_lines:
            # Truncate by visual width if line is too long
            if visual_width(line) > bubble_width - 4:
                # Truncate character by character until it fits
                truncated_line = line
                for i in range(len(line), 0, -1):
                    if visual_width(line[:i]) <= bubble_width - 4:
                        truncated_line = line[:i]
                        break
            else:
                truncated_line = line
            
            # Use visual padding for proper alignment
            content_width = bubble_width - 4
            padded_content = ljust_visual(truncated_line, content_width)
            # Create bubble content line (same pattern as guest messages)
            bubble_content = f"│ {padded_content} │"
            # Build line: outer border + padding + bubble + space + final border
            line_so_far = f"│{' ' * bubble_padding}{bubble_content}"
            remaining_space = chat_width - visual_width(line_so_far) - 1  # -1 for final │
            result.append(f"{line_so_far} │")
        result.append(f"│{' ' * bubble_padding}╰{'─' * (bubble_width-2)}╯ │")
    else:
        # Left-aligned guest messages
        header = f"{username} {timestamp}"
        # Use visual width for accurate calculation
        header_width = visual_width(header)
        header_spaces = max(0, (chat_width - 3) - header_width)
        result.append(f"│ {header}{' ' * header_spaces}│")
        
        # Bubble with proper alignment
        result.append(f"│ ╭{'─' * (bubble_width-2)}╮{' ' * (chat_width-bubble_width-3)}│")
        for line in wrapped_lines:
            # Truncate by visual width if line is too long
            if visual_width(line) > bubble_width - 4:
                # Truncate character by character until it fits
                truncated_line = line
                for i in range(len(line), 0, -1):
                    if visual_width(line[:i]) <= bubble_width - 4:
                        truncated_line = line[:i]
                        break
            else:
                truncated_line = line
            
            # Use visual padding for proper alignment
            content_width = bubble_width - 4
            padded_content = ljust_visual(truncated_line, content_width)
            # Create complete bubble content line that's exactly bubble_width columns
            bubble_content = f"│ {padded_content} │"
            # Add to result: outer border + space + bubble + fill to chat_width
            line_so_far = f"│ {bubble_content}"
            remaining_space = chat_width - visual_width(line_so_far) - 1  # -1 for final │
            result.append(f"{line_so_far}{' ' * max(0, remaining_space)}│")
        result.append(f"│ ╰{'─' * (bubble_width-2)}╯{' ' * (chat_width-bubble_width-3)}│")
    
    return result


def create_chat_interface(comments: List[dict], chat_width: int = 50, 
                         title: str = "#builders-chat", issue_number: str = "1", 
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
        if i > 0:
            lines.extend(canvas.create_spacer())
        
        username = comment['user']['login']
        content = comment['body']
        timestamp = comment.get('created_at', '')
        is_owner = comment.get('is_owner', False)  # Use pre-computed owner status
        
        # Format timestamp (simplified)
        if timestamp:
            try:
                from dateutil import parser as date_parser
                dt = date_parser.parse(timestamp)
                formatted_time = dt.strftime('%H:%M')
            except:
                formatted_time = '??:??'
        else:
            formatted_time = '??:??'
        
        bubble_lines = _create_message_bubble(
            content, username, formatted_time, is_owner, 
            chat_width, max_lines=max_lines, issue_number=issue_number
        )
        lines.extend(bubble_lines)
    
    # Footer
    lines.extend(canvas.create_spacer())
    lines.extend(canvas.create_footer(issue_number))
    
    return '\n'.join(lines)