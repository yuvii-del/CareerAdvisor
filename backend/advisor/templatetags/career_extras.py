"""
Template helpers for career guidance display.
"""

import re

from django import template

from advisor.career_normalize import normalize_required_skills as _normalize_required_skills

register = template.Library()


@register.filter
def required_skills_list(value):
    """Flatten comma/newline-joined skills for chip UI."""
    return _normalize_required_skills(value)


@register.filter
def learning_path_steps(value):
    """
    Split a long learning_path string into discrete steps for bullet lists.
    Handles arrows, newlines, bullets, semicolons, and numbered items.
    """
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []

    # Numbered list: "1. foo 2. bar"
    if re.search(r"\d+\.\s+", s):
        chunks = re.split(r"(?=\d+\.\s+)", s)
        out = [c.strip() for c in chunks if c.strip()]
        if len(out) > 1:
            return out

    # Common separators: arrows, bullets, newlines, semicolon+space
    parts = re.split(
        r"\s*(?:→|->|⟹|•|·|\n+|;\s+)(?=\S)",
        s,
    )
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) > 1:
        return parts

    # Long single line: split on " - " when it looks like a chain
    if len(s) > 60 and " - " in s:
        dash_parts = [p.strip() for p in re.split(r"\s+-\s+", s) if p.strip()]
        if len(dash_parts) > 1:
            return dash_parts

    return [s]
