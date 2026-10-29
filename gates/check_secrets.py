#!/usr/bin/env python3
"""Check that no tracked file matches a common secret pattern."""
import re

import common

PATTERNS = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("API key (sk-)", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]


def check(root, files):
    errors = []
    scanned = 0
    for rel in files:
        text = common.read_text(root, rel)
        if text is None:
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            for label, regex in PATTERNS:
                if regex.search(line):
                    errors.append("%s:%d: possible secret (%s)" % (rel, number, label))
    return errors, ["files scanned: %d" % scanned]


if __name__ == "__main__":
    common.main("secrets", check)
