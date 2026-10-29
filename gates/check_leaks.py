#!/usr/bin/env python3
"""Check that tracked text files hold no local paths or internal terms.

Terms come from gates/leak-terms.txt. A line is a case-insensitive literal.
A line that starts with "re:" is a regular expression.
Exceptions come from gates/leak-allow.txt, one "path:term" per line.
"""
import os
import re

import common

TERMS_FILE = os.path.join(common.GATES_DIR, "leak-terms.txt")
ALLOW_FILE = os.path.join(common.GATES_DIR, "leak-allow.txt")
SELF_FILES = ("gates/leak-terms.txt", "gates/leak-allow.txt")


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        lines = [l.rstrip("\n") for l in handle]
    return [l for l in lines if l.strip() and not l.startswith("#")]


def load_terms(path=TERMS_FILE):
    """Return a list of (label, compiled regex)."""
    terms = []
    for line in read_lines(path):
        if line.startswith("re:"):
            pattern = line[3:]
            terms.append((pattern, re.compile(pattern)))
        else:
            terms.append((line, re.compile(re.escape(line), re.IGNORECASE)))
    return terms


def load_allow(path=ALLOW_FILE):
    allowed = set()
    for line in read_lines(path):
        rel, _, term = line.partition(":")
        allowed.add((rel, term))
    return allowed


def check(root, files, terms=None, allowed=None):
    terms = load_terms() if terms is None else terms
    allowed = load_allow() if allowed is None else allowed
    errors = []
    scanned = 0
    for rel in files:
        if rel in SELF_FILES or os.path.basename(rel).startswith("LICENSE-"):
            continue
        text = common.read_text(root, rel)
        if text is None:
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            for label, regex in terms:
                if regex.search(line) and (rel, label) not in allowed:
                    errors.append("%s:%d: leak term %r" % (rel, number, label))
    return errors, ["text files scanned: %d" % scanned]


if __name__ == "__main__":
    common.main("leaks", check)
