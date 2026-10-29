#!/usr/bin/env python3
"""Check that tracked text files hold no local paths or internal terms.

Generic terms come from gates/leak-terms.txt. A line is a case-insensitive literal.
A line that starts with "re:" is a regular expression.
Private terms come from gates/leak-terms.local.txt when that file is present.
The local file is not tracked. The real run says whether it was read.
Exceptions come from gates/leak-allow.txt, one "path:term" per line.
The selftest does not read the local file. A fixture tree may hold a support
file named _terms.txt, which adds synthetic terms for that tree only.
Licence files are scanned like any other text file.
"""
import os
import re

import common

TERMS_FILE = os.path.join(common.GATES_DIR, "leak-terms.txt")
LOCAL_TERMS_FILE = os.path.join(common.GATES_DIR, "leak-terms.local.txt")
ALLOW_FILE = os.path.join(common.GATES_DIR, "leak-allow.txt")
SELF_FILES = ("gates/leak-terms.txt", "gates/leak-allow.txt", "gates/leak-terms.local.txt")
FIXTURE_TERMS = "_terms.txt"


def read_lines(path):
    with open(path, encoding="utf-8") as handle:
        lines = [l.rstrip("\n") for l in handle]
    return [l for l in lines if l.strip() and not l.startswith("#")]


def compile_terms(lines):
    """Return a list of (label, compiled regex)."""
    terms = []
    for line in lines:
        if line.startswith("re:"):
            pattern = line[3:]
            terms.append((pattern, re.compile(pattern)))
        else:
            terms.append((line, re.compile(re.escape(line), re.IGNORECASE)))
    return terms


def load_terms(path=TERMS_FILE):
    return compile_terms(read_lines(path))


def load_allow(path=ALLOW_FILE):
    allowed = set()
    for line in read_lines(path):
        rel, _, term = line.partition(":")
        allowed.add((rel, term))
    return allowed


def check(root, files, terms=None, allowed=None):
    notes = []
    if terms is None:
        terms = load_terms()
        fixture_terms = os.path.join(root, FIXTURE_TERMS)
        if root != common.ROOT:
            if os.path.isfile(fixture_terms):
                terms += compile_terms(read_lines(fixture_terms))
                notes.append("fixture terms read: " + FIXTURE_TERMS)
        elif os.path.isfile(LOCAL_TERMS_FILE):
            local = load_terms(LOCAL_TERMS_FILE)
            terms += local
            notes.append("local terms file read: gates/leak-terms.local.txt (%d terms)" % len(local))
        else:
            notes.append("local terms file absent: gates/leak-terms.local.txt; only generic terms were applied")
    allowed = load_allow() if allowed is None else allowed
    errors = []
    scanned = 0
    for rel in files:
        if rel in SELF_FILES or os.path.basename(rel) == FIXTURE_TERMS:
            continue
        text = common.read_text(root, rel)
        if text is None:
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            for label, regex in terms:
                if regex.search(line) and (rel, label) not in allowed:
                    errors.append("%s:%d: leak term %r" % (rel, number, label))
    notes.append("text files scanned: %d" % scanned)
    return errors, notes


if __name__ == "__main__":
    common.main("leaks", check)
