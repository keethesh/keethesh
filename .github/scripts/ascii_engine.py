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

        # Second line – shell / user meta info
        meta = (
            f"Last activity: {datetime.datetime.now():%H:%M:%S} | "
            "Shell: /bin/bash | "
            f"Users: {participant_count} | [Scroll: ^^^]"
        )
        lines.append("|" + _clip(meta, self._inner_width()) + "|")
        lines.append(self._border())
        return lines

    # .......................................................................
    def create_footer(self, issue_number: str) -> List[str]:
        """Return terminal window footer with just the terminal interface."""
        footer: List[str] = []

        status = (
            "--- Terminal Session Active --- Press Ctrl+C to exit --- "
            f"Connected to Issue #{issue_number} ---"
        )
        footer.append(_clip(status, self.width))

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

    # MESSAGES with spacing between each comment
    for i, c in enumerate(comments):
        # Add blank line before each message (except the first)
        if i > 0:
            pieces.append(_clip("", chat_width))  # Empty line between messages
            
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

    # TERMINAL FOOTER
    pieces.extend(canvas.create_footer(issue_number))

    return "\n".join(pieces)
