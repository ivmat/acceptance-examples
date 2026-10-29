#!/usr/bin/env python3
"""Check that relative links in tracked Markdown files resolve to tracked paths.

Inline links `[text](target)` and reference-style links are checked.
A reference-style link is `[text][ref]` or `[ref][]` with a definition line
`[ref]: target`. The target of each definition is checked, and so is each
use whose reference has no definition.
"""
import os
import posixpath
import re
from urllib.parse import unquote

import common

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_USE_RE = re.compile(r"!?\[([^\]]*)\]\[([^\]]*)\]")
REF_DEF_RE = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+.*)?$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
SKIP_SCHEMES = ("http://", "https://", "mailto:")


def norm_label(label):
    return " ".join(label.split()).lower()


def check_target(rel, number, target, file_set, dir_set):
    """Return (counted, error) for one link target."""
    if target.lower().startswith(SKIP_SCHEMES) or target.startswith("#"):
        return False, None
    path = unquote(re.split(r"[#?]", target, maxsplit=1)[0])
    if not path:
        return False, None
    if path.startswith("/"):
        resolved = posixpath.normpath(path.lstrip("/"))
    else:
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
    ok = resolved in file_set or resolved.rstrip("/") in dir_set
    if resolved.startswith("..") or not ok:
        return True, "%s:%d: broken link: %s" % (rel, number, target)
    return True, None


def check(root, files):
    errors = []
    file_set = set(files)
    dir_set = set()
    for f in files:
        parent = posixpath.dirname(f)
        while parent:
            dir_set.add(parent)
            parent = posixpath.dirname(parent)
    dir_set.add("")
    count = 0
    for rel in files:
        if not rel.endswith(".md"):
            continue
        text = common.read_text(root, rel)
        if text is None:
            continue
        in_fence = False
        defs = {}
        uses = []
        for number, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            definition = REF_DEF_RE.match(line)
            if definition:
                label = norm_label(definition.group(1))
                defs.setdefault(label, (number, definition.group(2)))
                continue
            stripped = CODE_SPAN_RE.sub("", line)
            for match in LINK_RE.finditer(stripped):
                counted, error = check_target(rel, number, match.group(1), file_set, dir_set)
                count += counted
                if error:
                    errors.append(error)
            for match in REF_USE_RE.finditer(stripped):
                label = norm_label(match.group(2) or match.group(1))
                uses.append((number, label))
        for label, (number, target) in sorted(defs.items(), key=lambda item: item[1][0]):
            counted, error = check_target(rel, number, target, file_set, dir_set)
            count += counted
            if error:
                errors.append(error)
        for number, label in uses:
            if label not in defs:
                errors.append("%s:%d: reference link has no definition: [%s]" % (rel, number, label))
    return errors, ["relative links checked: %d" % count]


if __name__ == "__main__":
    common.main("links", check)
