"""Secret patterns shared by check.py (scanning) and sessions.py (redacting). Standard library only."""

import re

# Specific token shapes: precise enough to scan code with few false alarms.
TOKENS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI-style key", re.compile(r"\bsk-(?!ant-)(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}")),
    ("Stripe key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Hugging Face token", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
]

# Shapes that are normal in code (public anon JWTs, local dev database URLs) but must not be
# echoed from a chat transcript: used for redacting only, not for scanning.
REDACT_ONLY = [
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),  # JWT
    re.compile(r"(?<=://)[^/\s:@]+:[^/\s@]+(?=@)"),  # user:password@ in URLs
    re.compile(r"(?i)(?<=bearer )[A-Za-z0-9._~+/=-]{16,}"),  # Authorization: Bearer …
]

# "SOME_KEY=value" style assignments.
ASSIGNMENT = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:key|secret|token|passw(?:or)?d|pwd|credential)[A-Z0-9_]*\s*[:=]\s*['\"]?)"
    r"([^\s'\"]{8,})"
)


def find_tokens(text):
    """Yield the names of token patterns found in text (never the values)."""
    for name, pattern in TOKENS:
        if pattern.search(text):
            yield name


def redact(text):
    for _, pattern in TOKENS:
        text = pattern.sub("[REDACTED]", text)
    for pattern in REDACT_ONLY:
        text = pattern.sub("[REDACTED]", text)
    return ASSIGNMENT.sub(lambda m: m.group(1) + "[REDACTED]", text)
