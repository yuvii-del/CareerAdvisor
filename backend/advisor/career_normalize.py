"""
Normalize career recommendation fields from AI/JSON (often messy strings).
"""

from __future__ import annotations

import re
from typing import Any, List

def _split_one_skill_blob(blob: str) -> List[str]:
    s = (blob or "").strip()
    if not s:
        return []
    # One skill per line is common from models
    if "\n" in s or "\r" in s:
        parts: List[str] = []
        for line in re.split(r"[\r\n]+", s):
            parts.extend(_split_one_skill_blob(line))
        return parts
    if "," in s:
        return [p.strip() for p in s.split(",") if p.strip()]
    return [s]


def normalize_required_skills(value: Any) -> List[str]:
    """
    Turn required_skills into a clean list of strings.
    Handles: JSON string instead of array, comma-joined entries, newlines.
    """
    if value is None:
        return []

    raw: List[str] = []
    if isinstance(value, str):
        raw.extend(_split_one_skill_blob(value))
    elif isinstance(value, (list, tuple)):
        for item in value:
            if item is None:
                continue
            if isinstance(item, str):
                raw.extend(_split_one_skill_blob(item))
            else:
                t = str(item).strip()
                if t:
                    raw.extend(_split_one_skill_blob(t))
    else:
        raw.extend(_split_one_skill_blob(str(value)))

    seen: set[str] = set()
    out: List[str] = []
    for x in raw:
        x = x.strip()
        if not x:
            continue
        key = x.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out
