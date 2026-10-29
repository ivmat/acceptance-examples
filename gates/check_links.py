#!/usr/bin/env python3
"""Check that relative links in tracked Markdown files resolve to tracked paths."""
import os
import posixpath
import re
from urllib.parse import unquote

import common

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
SKIP_SCHEMES = ("http://", "https://", "mailto:")


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
        for number, line in enumerate(text.splitlines(), start=1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_RE.finditer(CODE_SPAN_RE.sub("", line)):
                target = match.group(1)
                if target.lower().startswith(SKIP_SCHEMES) or target.startswith("#"):
                    continue
                path = unquote(re.split(r"[#?]", target, maxsplit=1)[0])
                if not path:
                    continue
                if path.startswith("/"):
                    resolved = posixpath.normpath(path.lstrip("/"))
                else:
                    resolved = posixpath.normpath(
                        posixpath.join(posixpath.dirname(rel), path))
                count += 1
                ok = resolved in file_set or resolved.rstrip("/") in dir_set
                if resolved.startswith("..") or not ok:
                    errors.append("%s:%d: broken link: %s" % (rel, number, target))
    return errors, ["relative links checked: %d" % count]


if __name__ == "__main__":
    common.main("links", check)
