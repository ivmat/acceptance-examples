#!/usr/bin/env python3
"""Run each implementations/*/*/run_all.sh from its own directory."""
import os
import re
import subprocess

import common

PACKAGE_RE = re.compile(r"^implementations/[^/]+/[^/]+/run_all\.sh$")
TIMEOUT_SECONDS = 3600


def check(root, files):
    errors, notes = [], []
    scripts = [f for f in files if PACKAGE_RE.match(f)]
    if not scripts:
        notes.append("no packages")
    for rel in scripts:
        cwd = os.path.join(root, os.path.dirname(rel))
        try:
            result = subprocess.run(
                ["bash", "run_all.sh"], cwd=cwd,
                stdin=subprocess.DEVNULL, capture_output=True,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            errors.append(rel + ": timed out")
            continue
        if result.returncode == 0:
            notes.append(rel + ": exit 0")
        else:
            errors.append("%s: exit %d" % (rel, result.returncode))
            tail = result.stdout.decode("utf-8", "replace").splitlines()[-5:]
            errors.extend("    " + l for l in tail)
    return errors, notes


if __name__ == "__main__":
    common.main("packages", check)
