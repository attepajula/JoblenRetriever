"""
Smart description trimmer.

Skips the typical company intro boilerplate (About Us, mission statements,
founding story) and returns the first meaningful chunk of the actual job content.
"""

import re

# Patterns that signal company intro / boilerplate — skip these paragraphs
_INTRO_PATTERNS = re.compile(
    r"""
    \babout\s+\w+\b               # "About Wolt", "About the company"
    | \bwe\s+(are|create|build|help|have\s+been|were\s+founded|offer)\b
    | \bour\s+(mission|vision|values|culture|company|story|team\s+of\b)
    | \bfounded\s+in\b
    | \bwe'?re\s+a\s+\w+\s+company\b
    | \bjoined\s+forces\b
    | \bjoin\s+(us|our\s+team)\b
    | \bin\s+20\d\d\s+we\b        # "In 2014 we started"
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Patterns that signal actual job content — start here
_JOB_CONTENT_PATTERNS = re.compile(
    r"""
    \byou'?(\s*ll|re|\s+will)\b   # "you'll", "you will", "you're"
    | \bwe'?re\s+looking\b
    | \bwe\s+are\s+looking\b
    | \brequirements?\b
    | \bresponsibilities\b
    | \bwhat\s+you'?(\s*ll|\s+will|\s+bring)\b
    | \babout\s+the\s+role\b
    | \bthe\s+role\b
    | \byour\s+(background|qualifications?|skills?|experience)\b
    | \bwhat\s+we'?re?\s+(looking|expect|need)\b
    | \bqualifications?\b
    | \bwho\s+you\s+are\b
    | \bwhat\s+you\s+do\b
    """,
    re.VERBOSE | re.IGNORECASE,
)

MAX_CHARS = 400


def trim(text: str | None) -> str | None:
    if not text:
        return None

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paragraphs:
        return None

    # Find the first paragraph that looks like job content
    start = 0
    for i, para in enumerate(paragraphs):
        if _JOB_CONTENT_PATTERNS.search(para):
            start = i
            break
        # If it clearly matches intro patterns, skip it
        if _INTRO_PATTERNS.search(para):
            start = i + 1

    useful = paragraphs[start:]
    if not useful:
        useful = paragraphs  # fallback: return everything

    joined = " ".join(useful)

    if len(joined) <= MAX_CHARS:
        return joined

    # Truncate at word boundary
    truncated = joined[:MAX_CHARS]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] + "…" if last_space > 0 else truncated + "…"
