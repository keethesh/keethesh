#!/usr/bin/env python3
"""
Rich‑Powered ASCII Engine for Chat Interfaces  ✨
------------------------------------------------------------------------
Refactored to eliminate width overflows, ragged borders, and stray “|”
cursor markers.  Lines are now clipped or padded exactly to the user‑set
canvas width (defaults to 80).  Header / footer strings are truncated
intelligently so the frame never breaks, even when very long shell paths
or timestamps appear.

Public API
==========
    create_chat_interface() – Render a complete terminal‑style chat pane

Key Improvements
----------------
* Consistent measurement of visible width via wcwidth.
* New _clip() helper ensures **every** line respects the canvas width.
* Header / footer builders shorten overly‑long meta strings instead of
  letting them bleed past the right border.
* Message bubbles no longer append the stray “ |” cursor marker that was
  producing a dangling vertical bar on wrapped lines.
* Safer calculation of continuation prompts for wrapped text.
* Unit‑tested with CJK, emoji, and combining characters.
"""

from __future__ import annotations

import datetime
import textwrap
from dataclasses import dataclass
from typing import List

from wcwidth import wcswidth

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def visual_width(txt: str) -> int:
    """Return how many terminal columns *txt* occupies (Unicode‑aware)."""
    width = wcswidth(txt)
    # Some control / private‑use code‑points return ‑1; fall back to len.
    return width if width and width > 0 else len(txt)


def _clip(txt: str, width: int) -> str:
    """Trim *txt* so its visual width is **<=** *width*.

    When the text is shorter, it is right‑padded with spaces so callers
    can rely on an exact width.
    """
    if visual_width(txt) <= width:
        return txt + " " * (width - visual_width(txt))

    # Hard clip with ellipsis if there is room for it.
    ellipsis = "…"
    if width >= 1:
        truncated: str = ""
        for ch in txt:
            if visual_width(truncated + ch + ellipsis) > width:
                break
            truncated += ch
        return truncated + ellipsis + " " * (width - visual_width(truncated + ellipsis))
    return ""  # width == 0, unreachable in practice


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class _ChatCanvas:
    width: int = 80  # **total** width including frame characters
    title: str = "#readme-chat"

    # ────────────────────────────────────────────────────────────────────────
    # Header / Footer helpers
    # ────────────────────────────────────────────────────────────────────────

    def _inner_width(self) -> int:
        return self.width - 2  # account for leading/closing frame char

    def _border(self, char: str = "-") -> str:
        return "+" + char * (self.width - 2) + "+"

    # .......................................................................
    def create_header(self, participant_count: int) -> List[str]:
        """Return a list of strings that build the framed header box."""
        lines: List[str] = [self._border()]

        # Title bar with faux window controls
        controls = "[_] [^] [X] "
        title_txt = f"Terminal - {self.title}"
        inner = controls + title_txt
        title_line = "|" + _clip(inner, self._inner_width()) + "|"
        lines.append(title_line)

        # Enhanced system information with project context
        current_time = datetime.datetime.now()
        if participant_count == 0:
            meta = (
                f"Session: {current_time:%H:%M:%S} | Ready for connections | "
                "Projects: 3 active | Status: Building [ACTIVE]"
            )
        elif participant_count == 1:
            meta = (
                f"Active: {current_time:%H:%M:%S} | 1 contributor online | "
                "Mode: Development | Stack: Python+TS+Unity"
            )
        else:
            meta = (
                f"Live chat: {current_time:%H:%M:%S} | {participant_count} users | "
                "Collaboration mode | All welcome!"
            )
        lines.append("|" + _clip(meta, self._inner_width()) + "|")
        lines.append(self._border())
        
        # Add contextual welcome prompt based on activity level  
        if participant_count == 0:
            welcome_line = "keethesh@github:~/readme-chat (main)$ # Welcome! Start a conversation..."
        elif participant_count == 1:
            welcome_line = "keethesh@github:~/readme-chat (main)$ # Building in public - join the discussion!"
        else:
            welcome_line = f"keethesh@github:~/readme-chat (main)$ # {participant_count} contributors collaborating"
            
        lines.append(_clip(welcome_line, self.width))
        return lines

    # .......................................................................
    def create_footer(self, issue_number: str) -> List[str]:
        """Return terminal window footer with just the terminal interface."""
        footer: List[str] = []

        # Dynamic status based on activity
        status = (
            f"=== Live Terminal Session === Connected to Issue #{issue_number} === "
            "Share ideas, ask questions, collaborate ==="
        )
        footer.append(_clip(status, self.width))
        
        # Encouraging call-to-action
        cta_line = "keethesh@github:~/readme-chat (main)$ echo 'Your voice matters - join the conversation!'"
        footer.append(_clip(cta_line, self.width))

        prompt = "keethesh@github:~/readme-chat (main)$ _"
        footer.append(_clip(prompt, self.width))
        footer.append(self._border())
        return footer
    


# ---------------------------------------------------------------------------
# Message Bubble builder
# ---------------------------------------------------------------------------

def _create_message_bubble(
    content: str,
    username: str,
    _timestamp: str,  # kept for signature compatibility, unused after refactor
    is_owner: bool = False,
    chat_width: int = 80,
    max_lines: int = 4,
    issue_number: str = "1",
) -> List[str]:
    """Return the visual representation of a single chat message."""

    current_time = datetime.datetime.now().strftime("%H:%M")

    base_prompt = (
        f"[{current_time}] {username}@github:~/readme-chat (main)$ # "
        if is_owner
        else f"[{current_time}] {username}@github:~$ # "
    )

    prompt_width = visual_width(base_prompt)
    available = max(1, chat_width - prompt_width)  # sane minimum of 1 col

    # Wrap paragraphs while respecting Unicode width.
    wrapped: List[str] = []
    for paragraph in content.split("\n"):
        if not paragraph.strip():
            wrapped.append("")  # preserve blank lines
            continue
        for line in textwrap.wrap(
            paragraph.strip(),
            width=available,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=True,
            break_long_words=True,
            break_on_hyphens=True,
        ):
            wrapped.append(line)

    # Truncate display to max_lines with a polite indicator.
    if len(wrapped) > max_lines:
        wrapped = wrapped[: max_lines - 1] + [f"[… see more at Issue #{issue_number}] <typing…>"]

    # Build visual lines.  Continuation prompt is just "> " indented.
    lines: List[str] = []
    cont_prompt = ">" + " " * (prompt_width - 1)

    for idx, segment in enumerate(wrapped):
        prompt = base_prompt if idx == 0 else cont_prompt
        line = prompt + segment
        lines.append(_clip(line, chat_width))

    return lines


# ---------------------------------------------------------------------------
# Public API – the function the rest of the project imports
# ---------------------------------------------------------------------------

def create_chat_interface(
    comments: List[dict],
    *,
    chat_width: int = 80,
    title: str = "#readme-chat",
    issue_number: str = "1",
    max_lines: int = 4,
) -> str:
    """Render the full chat interface as a single string."""

    canvas = _ChatCanvas(width=chat_width, title=title)
    pieces: List[str] = []

    # HEADER (framed)
    participant_count = len({c["user"]["login"] for c in comments}) if comments else 0
    pieces.extend(canvas.create_header(participant_count))

    # MESSAGES with intelligent spacing and context
    if not comments:
        # Enhanced empty state with project context
        pieces.extend([
            _clip("keethesh@github:~/readme-chat (main)$ # Welcome to the community chat!", chat_width),
            _clip("> This terminal connects to live GitHub Issue discussions", chat_width),
            _clip("> Share ideas, ask questions, collaborate on projects", chat_width),
            _clip("", chat_width),
            _clip("keethesh@github:~/readme-chat (main)$ git status", chat_width),
            _clip("On branch main", chat_width),
            _clip("Your branch is up to date with 'origin/main'.", chat_width),
            _clip("", chat_width),
            _clip("keethesh@github:~/readme-chat (main)$ ls -la projects/", chat_width),
            _clip("drwxr-xr-x  LookbackAI/     # AI-powered video journal SaaS", chat_width),
            _clip("drwxr-xr-x  Planify/        # Motion-style task planner", chat_width),
            _clip("drwxr-xr-x  MergeFleet/     # Unity space armada game", chat_width),
            _clip("", chat_width),
            _clip("keethesh@github:~/readme-chat (main)$ echo 'Join the conversation!'", chat_width),
            _clip("Join the conversation!", chat_width),
        ])
    else:
        for i, c in enumerate(comments):
            # Add contextual spacing and system info
            if i == 0 and len(comments) == 1:
                # Single message - add project context above
                pieces.extend([
                    _clip("keethesh@github:~/readme-chat (main)$ whoami", chat_width),
                    _clip("keethesh - Polymathic builder, CISSP, AI enthusiast", chat_width),
                    _clip("", chat_width),
                    _clip("keethesh@github:~/readme-chat (main)$ cat recent_activity.log", chat_width),
                    _clip("- Building LookbackAI: 94% facial recognition accuracy", chat_width),
                    _clip("- Developing Planify: skin-in-the-game productivity", chat_width),
                    _clip("- Prototyping MergeFleet: Unity mobile space strategy", chat_width),
                    _clip("", chat_width),
                ])
            elif i > 0:
                pieces.append(_clip("", chat_width))  # Standard spacing between messages
                
            pieces.extend(
                _create_message_bubble(
                    content=c["body"],
                    username=c["user"]["login"],
                    _timestamp=c.get("created_at", ""),
                    is_owner=c.get("is_owner", False),
                    chat_width=chat_width,
                    max_lines=max_lines,
                    issue_number=issue_number,
                )
            )
            
        # Add engagement context after messages
        if len(comments) <= 2:
            pieces.extend([
                _clip("", chat_width),
                _clip("keethesh@github:~/readme-chat (main)$ ps aux | grep inspiration", chat_width),
                _clip("Currently seeking: collaborators, feedback, interesting problems", chat_width),
                _clip("Stack: Python, TypeScript, React, Unity, AI/ML, Security Research", chat_width),
            ])

    # TERMINAL FOOTER
    pieces.extend(canvas.create_footer(issue_number))

    return "\n".join(pieces)
