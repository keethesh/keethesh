#!/usr/bin/env python3
"""
HTML-Powered Chat Engine for GitHub Profiles
===========================================
Modern HTML-based chat interface with better Unicode support,
styling flexibility, and responsive design capabilities.

Features:
- Clean HTML structure with CSS styling
- Better emoji and Unicode handling
- Responsive design
- Modern chat interface aesthetics
- GitHub-style theming
"""

import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
import html


@dataclass
class HtmlChatConfig:
    """Configuration for HTML chat interface"""
    max_width: str = "600px"
    theme: str = "github"
    show_timestamps: bool = True
    max_lines_per_message: int = 6
    enable_avatars: bool = False


def escape_html(text: str) -> str:
    """Safely escape HTML content"""
    return html.escape(text, quote=True)


def format_message_content(content: str, max_lines: int = 6, issue_number: str = "2") -> str:
    """Format message content with smart truncation"""
    if not content:
        return "<em>Empty message</em>"
    
    lines = content.strip().split('\n')
    
    if len(lines) > max_lines:
        truncated_lines = lines[:max_lines-1]
        truncated_content = '\n'.join(truncated_lines)
        return f"""{escape_html(truncated_content)}
<br><em><a href="https://github.com/{get_repo_path()}/issues/{issue_number}" target="_blank">
... see full comment in Issue #{issue_number}</a></em>"""
    
    return escape_html(content).replace('\n', '<br>')


def get_repo_path() -> str:
    """Get repository path from environment or default"""
    import os
    owner = os.environ.get('REPO_OWNER', 'keethesh')
    name = os.environ.get('REPO_NAME', 'keethesh')
    return f"{owner}/{name}"


def create_html_chat_interface(
    comments: List[Dict[str, Any]],
    *,
    config: HtmlChatConfig = None,
    title: str = "#readme-chat",
    issue_number: str = "2"
) -> str:
    """Create complete HTML chat interface"""
    
    if config is None:
        config = HtmlChatConfig()
    
    participant_count = len({c["user"]["login"] for c in comments}) if comments else 0
    current_time = datetime.datetime.now()
    
    # CSS Styles
    styles = """
<style>
.chat-container {
    max-width: 600px;
    margin: 0 auto;
    border: 1px solid #d1d9e0;
    border-radius: 8px;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.chat-header {
    background: linear-gradient(135deg, #f6f8fa 0%, #e1e8ed 100%);
    border-bottom: 1px solid #d1d9e0;
    padding: 12px 16px;
    border-radius: 8px 8px 0 0;
}

.window-controls {
    display: inline-flex;
    gap: 6px;
    margin-right: 12px;
    align-items: center;
}

.window-control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

.control-close { background: #ff5f57; }
.control-minimize { background: #ffbd2e; }
.control-maximize { background: #28ca42; }

.header-title {
    font-weight: 600;
    color: #24292f;
    display: inline;
}

.header-meta {
    font-size: 12px;
    color: #656d76;
    margin-top: 4px;
}

.chat-messages {
    padding: 16px;
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
}

.message {
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease-in;
}

.message:last-child {
    margin-bottom: 0;
}

.message-header {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
    gap: 8px;
}

.username {
    font-weight: 600;
    color: #0969da;
    font-size: 14px;
    text-decoration: none;
    transition: color 0.2s ease;
}

.username:hover {
    text-decoration: underline;
}

.username.owner {
    color: #8250df;
}

.username.owner:hover {
    color: #6639ba;
}

.timestamp {
    font-size: 12px;
    color: #656d76;
}

.message-content {
    background: #f6f8fa;
    padding: 8px 12px;
    border-radius: 8px;
    border-left: 3px solid #d1d9e0;
    line-height: 1.4;
    color: #24292f;
}

.message.owner .message-content {
    background: #dbeafe;
    border-left-color: #0969da;
}

.empty-state {
    text-align: center;
    padding: 32px 16px;
    color: #656d76;
}

.project-showcase {
    background: #f6f8fa;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
    border-left: 3px solid #fd8c73;
}

.project-item {
    margin: 6px 0;
    font-size: 14px;
}

.chat-footer {
    background: #f6f8fa;
    border-top: 1px solid #d1d9e0;
    padding: 12px 16px;
    border-radius: 0 0 8px 8px;
    text-align: center;
    font-size: 14px;
    color: #656d76;
}

.join-link {
    color: #0969da;
    text-decoration: none;
    font-weight: 500;
}

.join-link:hover {
    text-decoration: underline;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .chat-container {
        background: #0d1117;
        border-color: #30363d;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border-bottom-color: #30363d;
    }
    
    .header-title { color: #f0f6fc; }
    .header-meta { color: #8b949e; }
    
    .message-content {
        background: #161b22;
        border-left-color: #30363d;
        color: #f0f6fc;
    }
    
    .message.owner .message-content {
        background: #0c2d6b;
        border-left-color: #1f6feb;
    }
    
    .username { color: #58a6ff; }
    .username:hover { color: #79c0ff; }
    .username.owner { color: #a5a3ff; }
    .username.owner:hover { color: #b8b5ff; }
    .timestamp { color: #8b949e; }
    
    .project-showcase {
        background: #161b22;
        border-left-color: #f85149;
    }
    
    .chat-footer {
        background: #161b22;
        border-top-color: #30363d;
        color: #8b949e;
    }
}
</style>
"""
    
    # Build HTML structure
    html_parts = [styles]
    
    html_parts.append('<div class="chat-container">')
    
    # Header
    if participant_count == 0:
        status_text = f"Ready for connections • {current_time:%H:%M:%S}"
    elif participant_count == 1:
        status_text = f"1 contributor online • {current_time:%H:%M:%S}"
    else:
        status_text = f"{participant_count} users active • {current_time:%H:%M:%S}"
    
    html_parts.extend([
        '<div class="chat-header">',
        '<div class="window-controls">',
        '<span class="window-control control-close"></span>',
        '<span class="window-control control-minimize"></span>',
        '<span class="window-control control-maximize"></span>',
        '</div>',
        f'<div class="header-title">{escape_html(title)}</div>',
        f'<div class="header-meta">{escape_html(status_text)}</div>',
        '</div>'
    ])
    
    # Messages area
    html_parts.append('<div class="chat-messages">')
    
    if not comments:
        # Empty state with project showcase
        html_parts.extend([
            '<div class="empty-state">',
            '<h3>👋 Welcome to the community chat!</h3>',
            '<p>This is where GitHub Issue discussions come to life.</p>',
            '<div class="project-showcase">',
            '<div class="project-item">🧠 <strong>LookbackAI</strong> - AI-powered video journal SaaS</div>',
            '<div class="project-item">📋 <strong>Planify</strong> - Motion-style planner with skin in the game</div>',
            '<div class="project-item">🚀 <strong>MergeFleet</strong> - Unity mobile space armada game</div>',
            '</div>',
            '<p><em>Start a conversation to see messages appear here!</em></p>',
            '</div>'
        ])
    else:
        # Render messages
        for i, comment in enumerate(comments):
            username = comment["user"]["login"]
            is_owner = comment.get("is_owner", False)
            content = format_message_content(
                comment["body"], 
                config.max_lines_per_message, 
                issue_number
            )
            
            # Format timestamp
            timestamp = ""
            if config.show_timestamps and comment.get("created_at"):
                try:
                    from dateutil import parser as date_parser
                    dt = date_parser.parse(comment["created_at"])
                    timestamp = dt.strftime("%H:%M")
                except:
                    timestamp = ""
            
            owner_class = " owner" if is_owner else ""
            message_class = " owner" if is_owner else ""
            
            html_parts.extend([
                f'<div class="message{message_class}">',
                '<div class="message-header">',
                f'<a href="https://github.com/{escape_html(username)}" class="username{owner_class}" target="_blank">@{escape_html(username)}</a>',
                f'<span class="timestamp">{timestamp}</span>' if timestamp else '',
                '</div>',
                f'<div class="message-content">{content}</div>',
                '</div>'
            ])
    
    html_parts.append('</div>')  # End messages
    
    # Footer
    repo_path = get_repo_path()
    html_parts.extend([
        '<div class="chat-footer">',
        f'💬 <a href="https://github.com/{repo_path}/issues/{issue_number}" class="join-link" target="_blank">',
        f'Join the conversation in Issue #{issue_number}</a>',
        '</div>',
        '</div>'  # End container
    ])
    
    return '\n'.join(html_parts)