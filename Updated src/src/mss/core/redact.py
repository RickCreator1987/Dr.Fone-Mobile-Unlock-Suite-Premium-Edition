"""Redaction helpers.

Keeps PII out of logs and audit records. Callers must pass any free-form
string through `redact()` before writing it.
"""

from __future__ import annotations

import re

PATTERNS = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[email]"),
    (re.compile(r"\b(?:\+?\d[\s-]?){7,}\b"), "[phone]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[card]"),
    (re.compile(r"\b[A-F0-9]{8,}\b"), "[serial]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[ip]"),
]


def redact(value: str) -> str:
    out = value
    for pattern, replacement in PATTERNS:
        out = pattern.sub(replacement, out)
    return out